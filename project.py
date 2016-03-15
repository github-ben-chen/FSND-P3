from functools import wraps
from flask import Flask, g, render_template, request, redirect, jsonify, url_for, flash
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, CatalogItem, User
from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets, OAuth2Credentials, FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

app = Flask(__name__)

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Category Menu Application"


# Connect to Database and create database session
engine = create_engine('sqlite:///catalogwithusers.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# Create anti-forgery state token
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    # return "The current session state is %s" % login_session['state']
    return render_template('login.html', STATE=state)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'% access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['credentials'] = credentials.to_json()
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    # ADD PROVIDER TO LOGIN SESSION
    login_session['provider'] = 'google'

    # see if user exists, if it doesn't make a new one
    user_id = getUserID(data["email"])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in login_session:
            return redirect(url_for('showLogin', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def createUser(login_session):
    newUser = User(name=login_session['username'],
                   email=login_session['email'],
                   picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None

# DISCONNECT - Revoke a current user's token and reset their login_session


@app.route('/gdisconnect')
def gdisconnect():
    # Only disconnect a connected user.
    credentials = OAuth2Credentials.from_json(login_session.get('credentials'))
    if credentials is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = credentials.access_token
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] != '200':
        # For whatever reason, the given token was invalid.
        response = make_response(json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


# JSON APIs to view Category Information
@app.route('/catalog/<string:category_name>/JSON')
def categoryJSON(category_name):
    #category = session.query(Category).filter_by(id=category_id).one()
    items = session.query(CatalogItem).filter_by(name=category_name).all()
    return jsonify(CatalogItems=[i.serialize for i in items])


@app.route('/catalog/<string:category_name>/<string:item_name>/JSON')
def catalogItemJSON(category_name, item_name):
    Catalog_Item = session.query(CatalogItem).filter_by(name=item_name).one()
    return jsonify(Catalog_Item=Catalog_Item.serialize)


@app.route('/catalog/JSON')
def categoriesJSON():
    categories = session.query(Category).all()
    return jsonify(categories=[r.serialize for r in categories])


# Show all restaurants
@app.route('/')
@app.route('/catalog/')
def showCategories():
    categories = session.query(Category).order_by(asc(Category.name))
    items = session.query(CatalogItem).order_by(asc(CatalogItem.name))
    if 'username' not in login_session:
        return render_template('publiccategories.html', categories=categories,items=items)
    else:
        return render_template('categories.html', categories=categories,items=items)

@app.route('/catalog/new/', methods=['GET', 'POST'])
@login_required
def newCategory():
    # if 'username' not in login_session:
    #     return redirect('/login')
    if request.method == 'POST':
        newCategory = Category(name=request.form['name'], user_id=login_session['user_id'])
        session.add(newCategory)
        flash('New Category %s Successfully Created' % newCategory.name)
        session.commit()
        return redirect(url_for('showCategories'))
    else:
        return render_template('newCategory.html')

# Edit a restaurant


@app.route('/catalog/<string:category_name>/edit/', methods=['GET', 'POST'])
@login_required
def editCategory(category_name):
    editedCategory = session.query(Category).filter_by(name=category_name).one()
    # if 'username' not in login_session:
    #     return redirect('/login')
    if editedCategory.user_id != login_session['user_id']:
        return '''<script>function myFunction() {alert('You are not authorized to edit this category.
                  Please create your own category in order to edit.');}</script><body onload='myFunction()''>'''
    if request.method == 'POST':
        print "request.form['name']", request.form['name']
        if request.form['name']:
            editedCategory.name = request.form['name']
            flash('Category Successfully Edited %s' % editedCategory.name)
            return redirect(url_for('showCategories'))
    else:
        return render_template('editCategory.html', category=editedCategory)


# Delete a restaurant
@app.route('/catalog/<string:category_name>/delete/', methods=['GET', 'POST'])
@login_required
def deleteCategory(category_name):
    categoryToDelete = session.query(Category).filter_by(name=category_name).one()
    # if 'username' not in login_session:
    #     return redirect('/login')
    if categoryToDelete.user_id != login_session['user_id']:
        return '''<script>function myFunction() {alert('You are not authorized to delete this category.
                  Please create your own category in order to delete.');}</script><body onload='myFunction()''>'''
    if request.method == 'POST':
        session.delete(categoryToDelete)
        flash('%s Successfully Deleted' % categoryToDelete.name)
        session.commit()
        return redirect(url_for('showCategories', category_name=category_name))
    else:
        return render_template('deleteCategory.html', category=categoryToDelete)

# Show a restaurant menu

@app.route('/catalog/<string:category_name>/<string:item_name>')
def showCatalogItem(category_name, item_name):
    category = session.query(Category).filter_by(name=category_name).one()
    itemToShow = session.query(CatalogItem).filter_by(name=item_name).one()
    categories = session.query(Category).order_by(asc(Category.name))
    creator = getUserInfo(category.user_id)
    if 'username' not in login_session or creator.id != login_session['user_id']:
        return render_template('publicCatalogItem.html',category=category, categories=categories, item=itemToShow, creator=creator)
    else:
        return render_template('catalogItem.html', category=category, categories=categories, item=itemToShow, creator=creator)

@app.route('/catalog/<string:category_name>/')
def showMenu(category_name):
    category = session.query(Category).filter_by(name=category_name).one()
    categories = session.query(Category).order_by(asc(Category.name))
    creator = getUserInfo(category.user_id)
    items = session.query(CatalogItem).filter_by( category_name=category_name).all()
    if 'username' not in login_session or creator.id != login_session['user_id']:
        return render_template('publicCatalog.html', items=items, category=category, categories=categories, creator=creator)
    else:
        return render_template('catalog.html', items=items, category=category,categories=categories, creator=creator)


# Create a new menu item
@app.route('/catalog/<string:category_name>/item/new/', methods=['GET', 'POST'])
@login_required
def newCatalogItem(category_name):
    # if 'username' not in login_session:
    #     return redirect('/login')
    category = session.query(Category).filter_by(name=category_name).one()
    if login_session['user_id'] != category.user_id:
        return '''<script>function myFunction() {alert('You are not authorized to add item to this category.
                  Please create your own category in order to add items.');}</script><body onload='myFunction()''>'''
    if request.method == 'POST':
            print "here"
            print request.form['name']
            print request.form['description']
            newItem = CatalogItem(name=request.form['name'], description=request.form['description'], category_name=category_name, user_id=category.user_id)
            session.add(newItem)
            session.commit()
            flash('New Menu %s Item Successfully Created' % (newItem.name))
            return redirect(url_for('showMenu', category_name=category_name))
    else:
        return render_template('newCatalogItem.html', category=category)

# Edit a menu item


@app.route('/catalog/<string:category_name>/<string:item_name>/edit', methods=['GET', 'POST'])
@login_required
def editCatalogItem(category_name, item_name):
    # if 'username' not in login_session:
    #     return redirect('/login')
    editedItem = session.query(CatalogItem).filter_by(name=item_name).one()
    category = session.query(Category).filter_by(name=category_name).one()
    if login_session['user_id'] != category.user_id:
        return '''<script>function myFunction() {alert('You are not authorized to edit item to this category.
                  Please create your own category in order to edit items.');}</script><body onload='myFunction()''>'''
    if request.method == 'POST':
        if request.form['name']:
            editedItem.name = request.form['name']
        if request.form['description']:
            editedItem.description = request.form['description']
        session.add(editedItem)
        session.commit()
        flash('Menu Item Successfully Edited')
        return redirect(url_for('showMenu', category_name=category_name))
    else:
        return render_template('editCatalogItem.html', category=category, item=editedItem)


# Delete a menu item
@app.route('/catalog/<string:category_name>/<string:item_name>/delete', methods=['GET', 'POST'])
@login_required
def deleteCatalogItem(category_name, item_name):
    # if 'username' not in login_session:
    #     return redirect('/login')
    category = session.query(Category).filter_by(name=category_name).one()
    itemToDelete = session.query(CatalogItem).filter_by(name=item_name).one()
    if login_session['user_id'] != category.user_id:
        return '''<script>function myFunction() {alert('You are not authorized to delete menu items to this category.
                  Please create your own category in order to delete items.');}</script><body onload='myFunction()''>'''
    if request.method == 'POST':
        session.delete(itemToDelete)
        session.commit()
        flash('Menu Item Successfully Deleted')
        return redirect(url_for('showCategories', category_name=category_name))
    else:
        return render_template('deleteCatalogItem.html', category= category, item=itemToDelete)


# Disconnect based on provider
@app.route('/disconnect')
def disconnect():
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
            del login_session['gplus_id']
            del login_session['credentials']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        del login_session['provider']
        flash("You have successfully been logged out.")
        return redirect(url_for('showCategories'))
    else:
        flash("You were not logged in")
        return redirect(url_for('showCategories'))


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
