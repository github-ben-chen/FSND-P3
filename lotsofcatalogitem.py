# -*- coding: utf-8 -*-
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Category, Base, CatalogItem, User

engine = create_engine('sqlite:///catalogwithusers.db')


# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()

User1 = User(name="Ben Chen", email="bchen116@gmail.com",
             picture='https://lh3.googleusercontent.com/-vfAd6NphyQM/UnBuAffmzUI/AAAAAAAAAyo/4mZxs_gv8dc/w140-h140-p/10566890246_57f7bbf2f7.jpg')
session.add(User1)
session.commit()

category1 = Category(user_id=1, name="Snowboarding",id=1)

session.add(category1)
session.commit()

menuItem1 = CatalogItem(user_id=1, name="Snowboard", description='''Best for any terrain and conditions. All-mountain snowboards
                                                      perform anywhere on a mountain-groomed runs, backcountry, even park and pipe.
                                                      They maybe directional (meaning downhill only) or twin-tip (for riding swtich, meaning either direction).
                                                      Most boarders ride all-mountain boards. Because of their versatility, all-mountain boards are good for beginners who are still learning what terrain they like''',
                                                      category=category1,category_id =category1.id, category_name = category1.name)
session.add(menuItem1)
session.commit()

menuItem2 = CatalogItem(user_id=1,name="Goggles", description=''' Most modern cold-weather goggles have two layers of lens to prevent the interior from becoming "foggy". With only a single lens, the interior water vapor condenses onto the lens because the lens is colder than the vapor, although anti-fog agents can be used. The reasoning behind dual layer lens is that the inner lens will be warm while the outer lens will be cold. As long as the temperature of the inner lens is close to that of the interior water vapor, the vapor should not condense. However, if water vapor gets between the layers of the lens, condensation can occur between the lenses and is almost impossible to get rid of; thus, properly constructed and maintained dual-layer lenses should be air-tight to prevent water vapor from getting in between the lenses.''',
                                                      category=category1,category_id =category1.id, category_name = category1.name)
session.add(menuItem2)
session.commit()


category2 = Category(user_id=1,name="Soccer",id=2)

session.add(category2)
session.commit()

menuItem3 = CatalogItem(user_id=1,name="Soccer Cleats", description='''Cleats or studs are protrusions on the sole of a shoe, or on an external attachment to a shoe,
                                                                       that provide additional traction on a soft or slippery surface.
                                                                       In American English the term cleats is used synecdochically to refer to shoes featuring such protrusions.
                                                                       This does not happen in British English; the term 'studs' is never used to refer to the shoes, which would instead be known as 'football boots', 'rugby boots', and so on.''',
                                                      category=category2,category_id =category2.id, category_name = category2.name )
session.add(menuItem3)
session.commit()

menuItem4 = CatalogItem(user_id=1,name="Soccer Jersey", description=''' Soccer jerseys are an important piece of uniform for any soccer game.
                                                                        While a quick recreational game can be played in any athletic clothes,
                                                                        any soccer player can tell you that a good soccer jersey is necessary if you want to be comfortable and play at your best.''',
                                                      category=category2,category_id =category2.id, category_name = category2.name)
session.add(menuItem4)
session.commit()

menuItem5 = CatalogItem(user_id=1,name="Shinguards", description='''A shin guard or shin pad is a piece of equipment worn on the front of plyer's shine for protection''',
                                                      category=category2,category_id =category2.id, category_name = category2.name)
session.add(menuItem5)
session.commit()

category = Category(user_id=1,name="Basketball",id=3)

session.add(category)
session.commit()

menuItem = CatalogItem(user_id=1,name="Basketball", description=''' A basketball is a spherical inflated ball used in a game of basketball.
                                                                    Basketballs typically range in size from very small promotional items only a few inches in diameter to extra large balls nearly a foot in diameter used in training exercises to increase the skill of players.
                                                                    The standard size of a basketball in the NBA is 9.5 to 9.85 inches (24.1 to 25.0 cm) in diameter.''',
                                                      category=category, category_id =category.id, category_name = category.name)
session.add(menuItem)
session.commit()


category = Category(user_id=1,name="Frisbee",id=5)

session.add(category)
session.commit()

menuItem = CatalogItem(user_id=1,name="Frisbee (Flying disc)", description=''' A flying disc is a disc-shaped gliding toy or sporting item that is generally plastic and roughly 20 to 25 centimetres (8 to 10 in) in diameter with a lip,[1] used recreationally and competitively for throwing and catching, for example, in flying disc games. The shape of the disc, an airfoil in cross-section, allows it to fly by generating lift as it moves through the air while spinning. The term Frisbee, often used to generically describe all flying discs, is a registered trademark of the Wham-O toy company. Though such use is not encouraged by the company, the common use of the name as a generic term has put the trademark in jeopardy; accordingly, many "Frisbee" games are now known as "disc" games, like Ultimate or disc golf.''',
                                                      category=category, category_id =category.id, category_name = category.name)
session.add(menuItem)
session.commit()

category = Category(user_id=1,name="rock climbing",id=6)

session.add(category)
session.commit()

menuItem = CatalogItem(user_id=1,name="Climbing Ropes", description=''' Climbing ropes are typically of kernmantle construction, consisting of a core (kern) of long twisted fibres and an outer sheath (mantle) of woven coloured fibres. The core provides about 80% of the tensile strength, while the sheath is a durable layer that protects the core and gives the rope desirable handling characteristics.''',
                                                      category=category, category_id =category.id, category_name = category.name)
session.add(menuItem)
session.commit()

print "added menu items!"
