Catalog Project: this is a web application which provides a list of items of different categories. A third part user registration and authentication is also integrated (Google)

python version: 2.7.6
library needed: functools, flask, sqlalchemy, oauth2client, json

Step 1: setup and access the database:
    1.0)  cd /vagrant/tournament
    1.1)  vagrant up
    1.2)  vagrant ssh
    1.3)  cd /vagrant/catalog
	  1.4)  run python database_setup.py
    1.5)  run lotsofcatalogitem.py (optional, this is for the purpose of demonstration, users can start to contribute and build up the database once they login)
Step 2: run project.py
Step 3: navigate to http://localhost:5000/ in your browser
