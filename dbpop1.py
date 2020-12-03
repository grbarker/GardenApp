from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import requests
from app import create_app, db
from app.models import User, Plant, Garden, Post
import random


app = create_app()
app_context = app.app_context()
app_context.push()
db.create_all()

Base = declarative_base()
engine = create_engine('sqlite:///app.db')
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

gkey = 'AIzaSyBQ4vlq-6pxvlBXkxLbxkTszyiriWDAWeA'
plants = [
    'eggplant', 'chard', 'swisschard', 'rhubarb', 'peas', 'green peas', 'black bean', 'arugula',
    'sweet basil','basil','cinnoman basil','thai basil','cherry tomato','beefsteak tomoato',
    'supersweet 100 tomato','kale','beet','carrot','brocolli',
    'asparagus', 'black-eyed peas','artichoke', 'kidney beans', 'pinto beans', 'mung beans', 'split peas', 'soy beasn', 'brussels sprouts', 'cabbage', 'mustard greens', 'collard greens', 'spinach',
    'anise', 'caraway', 'dill', 'fennel', 'lavender', 'marjoram', 'lemon grass', 'parsley', 'sage', 'thyme',
    'lettuce', 'okra', 'white onion', 'yellow onion', 'red onion', 'chives', 'leek', 'garlic', 'shallot', 'scallion', 'green onions',
    'bell pepper', 'jalapeno', 'habanero', 'paprika', 'tobasco pepper', 'cayenne pepper', 'ghost pepper', 'celery',
    'water chestnut', 'ginger', 'parsnip', 'horseradish', 'daikon', 'wasabi', 'potato', 'sweet potato', 'yam',
    'sweetcorn', 'acorn squash', 'butternut squash', 'cucumber', 'spaghetti squash', 'banana squash',
    ' zucchini', 'bok choy', 'cauliflower'
]

posts = [
    'Hello!', 'How are you people doing?', 'How is everybody doing?', 'hello', 'hello!', 'Hello',
    'I just planted something!', "What's the weather like for everybod?", 'Happy planting!', "What's going on in the neighborhood?",
    'mmmm tomatoes', 'alright', "It's so nice outside today", "I'm back baby", "yarp", "narp"
]


addresses = [
    ['6820 SE 29th Ave, Portland, OR 97202','aya', 'bob', []],
    ['','gb', 'lordsburg', []],
    ['','gregor', 'thegreatest', []],
    ['','gregorius', 'thegreat', []],
    [
        '1214 SE 60th Ave, Portland, OR 97215',
        'bob',
        'thecat',
        [
            ['far back corner', ['kumquat']],
            ['back corner north', ['boxwood', 'privet', 'basil', 'thyme', 'lavender']],
            ['front streetside', ['flowering quince']],
            ['front yard', ['amur maple', 'japanese barberry', 'juniper', 'petunia', 'geranium', 'iris-purple']],
            ['side yard', ['japanese barberry', 'juniper', 'holly']]
        ]
    ],
    [
        '3401 NE Couch St, Portland, OR 97232',
        'hamburgler',
        'mcds',
        [
            ['front yard', ['geranium', 'petunia', 'ivy-irish', 'juniper']],
            ['side yard', ['ivy-english', 'ivy-irish', 'ivy-japanese']],
            ['side yard', ['geranium']],
        ]
    ],
    [
        '5830 SE 41st Ave, Portland, OR 97202',
        'cornelius',
        'cornelius',
        [
            ['front yard', ['holly', 'spinach', 'lavender', 'rosemary', 'sage']],
            ['side yard', ['orange', 'apple-granny smith', 'apple-honeycrisp', 'apple-gala']],
            ['side bed A', ['thyme', 'sage', 'rosemary', 'basil', 'thai basil', 'lavender']],
            ['side bed B', ['endive', 'kale', 'spinach', 'asparagus', 'fennel', 'arugula', 'caraway', 'cilantro']],
            ['side bed C', ['tomato-brandywine', 'tomato-cherokee purple', 'tomato-cherry', 'tomato-roma', 'chili pepper-habenero', 'chili pepper-serrano', 'chili pepper-jalapeno', 'chili pepper-fresno', 'chili pepper-ghost pepper', 'chili pepper-guajillo']],
        ]
    ],
    [
        '5304 SE 40th Ave, Portland, OR 97202',
        'wilhelm',
        'wilhelm',
        [
            ['corner', ['geranium', 'azalea', 'peony', 'petunia', 'ivy-english', 'ivy-algerian', 'ivy-irish', 'lavender', 'thyme', 'rosemary']],
            ['front yard', ['kumquat', 'orange', 'apple-honeycrisp', 'endive', 'kale', 'romaine lettuce', 'spinach', 'chard', 'rhubarb', 'brocolli', 'asparagus', 'peas']],
            ['back yard', ['raspberry', 'strawberry', 'blackberry', 'marionberry', 'blueberry']],
        ]
    ],
    [
        '6347 SE Yamhill St, Portland, OR 97215',
        'merwin',
        'merwin',
        [
            ['back north', ['thyme', 'lavender', 'hyacinth', 'endive', 'chard', 'spinach', 'kale', 'romaine lettuce', 'red cabbage', 'asparagus', 'raspberry', 'blackberry', 'marionberry' , 'marigold']],
            ['back south', ['lavender', 'peony', 'azalea', 'tomato-red beefsteak', 'tomato-cherry', 'tomato-better boy']],
            ['back yamhill', ['juniper', 'holly', 'laurel', 'maple']],
        ]
    ],
    [
        '5330 SE Cesar Estrada Chavez Blvd, Portland, OR 97202',
        'edmund',
        'edmund',
        [
            ['streetside yard', ['ivy-english', 'ivy-ivalace', 'ivy-irish']],
            ['side yard', ['orange', 'apple-honeycrisp', 'avocado', 'plum', 'kumquat']],
            ['side bed A', ['kale', 'spinach', 'endive', 'chard']],
            ['side bed B', ['thyme', 'sage', 'rosemary', 'lavender']],
            ['side bed C', ['basil', 'thai basil', 'cinnamon basil', 'anise']],
            ['back yard', ['tomato-roma', 'tomato-cherry', 'tomato-brandywine', 'tomato-red beefsteak']],
        ]
    ],
    [
        '1245 SE 60th Ave, Portland, OR 97215',
        'munster',
        'munster',
        [
            ['back corner bed A', ['tomato-cherry', 'tomato-red beefsteak', 'tomato-roma']],
            ['back corner bed B', ['tomato-cherry', 'tomato-red beefsteak', 'tomato-roma']],
            ['back corner bed C', ['tomato-cherry', 'tomato-chorokee', 'tomato-better boy']],
            ['back shaded', ['romaine lettuce', 'kale', 'endive', 'spinach']],
            ['front yard', []],
            ['back close in', []],
        ]
    ],
    [
        '907 SE Nehalem St, Portland, OR 97202',
        'wilbur',
        'wilbur',
        [
            ['back bed', ['anise', 'caraway', 'dill', 'fennel', 'lavender', 'marjoram', 'lemon grass', 'parsley', ]],
            ['streetside bed', ['eggplant', 'chard', 'swisschard', 'rhubarb', 'peas', 'green peas', 'arugula', 'bok choy',]],
            ['front yard', ['lavender', 'petunia', 'marigold', 'lantana']],
        ]
    ],
    [
        '6820 SE 29th Ave, Portland, OR 97202',
        'susan',
        'susan',
        [
            ['front yard', ['petunia', 'azalea']],
            ['side terrace', ['ivy-english', 'ivy-irish', 'ivy-algerian', 'ivy-ivalace', 'ivy-algerian', 'ivy-goldchild', 'thyme','rosemary', 'lavender']],
            ['back side', ['petunia', 'azalea', 'thyme', 'basil', 'rosemary']],
            ['patio', ['lantana', 'fuschia', 'geranium']],
            ['back yard', ['kale', 'chard', 'celery', 'rhubarb']],
        ]
    ],
    [
        '6213 SE Main St, Portland, OR 97215',
        'harold',
        'harold',
        [
            ['front yard', ['petunia', 'azalea']],
            ['side yard', ['kale', 'spinach', 'endive', 'romaine lettuce', 'thyme', 'basil', 'rosemary', 'avocado']],
            ['back yard', ['petunia', 'azalea', 'thyme', 'basil', 'rosemary']],
            ['back patio', ['petnuia', 'lantana', 'fuschia', 'geranium']],
            ['back yard', ['kale', 'spinach', 'chard', 'beet', 'rhubarb']],
        ]
    ],
    [
        '2937 SE Claybourne St, Portland, OR 97202',
        'jon',
        'jon',
        [
            ['side yard', ['kale', 'spinach', 'endive', 'romaine lettuce', 'thyme', 'basil', 'rosemary']],
            ['back yard', ['petunia', 'azalea']],
            ['front yard', ['kale', 'spinach', 'chard', 'beet', 'rhubarb']],
        ]
    ],
    [
        '5326 SE 40th Ave, Portland, OR 97202',
        'john',
        'john',
        [
            ['street end beds/pots', ['mini rose-red', 'mini rose-white', 'kumquat', 'wheatgrass', 'kale', 'spinach', 'chard']],
            ['back side', ['asparagus', 'onion-white', 'onion-red', 'scallion', 'chili pepper-serrano', 'chili pepper-habenero', 'chili pepper-jalapeno', 'chili pepper-guajillo']],
            ['fron yard', ['apple-granny smith', 'apple-honeycrisp', 'apple-gala']],
        ]
    ],
    [
        '1718 SE 16th Ave, Portland, OR 97214',
        'jeff',
        'jeff',
            ['front yard north', ['rose-red', 'rose-white', 'rose-black', 'rose-pink']],
            ['front yard south', ['rose-red', 'rose-white', 'rose-black']],
            ['side yard', ['kale', 'spinach', 'endive', 'romaine lettuce', 'thyme', 'basil', 'thai basil', 'rosemary', 'sage']],
            ['back yard', ['green beans', 'purple beans']],
            ['greenhouse', ['tomato-brandywine', 'tomato-roma', 'chili pepper-serrano', 'chili pepper-jalapeno', 'tomato-cherry','sage']],
    ],
    [
        '1930 SE 20th Ave, Portland, OR 97214',
        'richard',
        'richard',
        [
            ['front yard', ['lavender']],
            ['front side', ['rosemary', 'thyme']],
            ['back yard', ['apple-fuji']],
            ['back corner', ['kale', 'spinach', 'endive']],

        ]
    ],
    [
        '4927 SE 41st Ave, Portland, OR 97202',
        'evan',
        'evan',
        [
            ['front streetside', ['apple-fuji', 'apple-granny smith', 'apple-honeycrisp']],
            ['side yard', ['petunia', 'marigold', 'lantana', 'raspberry', 'strawberry']],
            ['back corner', ['kale', 'spinach', 'beet']],
            ['back yard', ['tomato-cherry', 'tomato-black krim', 'tomato-roma', 'tomato-indigo', 'tomato-brandywine', 'rose-white', 'rose-red']],
        ]
    ],
    [
        '5325 SE 40th Ave, Portland, OR 97202',
        'ethan',
        'ethan',
        [
            ['front yard', ['apple-fuji', 'apple-gala']],
            ['back yard', ['iris-purple', 'iris-white']],
            ['side yard', ['kale', 'spinach', 'beet']],
            ['greenhouse', ['tomato-cherry', 'tomato-black krim', 'tomato-roma', 'tomato-indigo', 'tomato-brandywine']],
        ]
    ],
    [
        '1209 SE 60th Ave, Portland, OR 97215',
        'alvin',
        'alvin',
        [
            ['back raised bed A', ['tomato-cherry']],
            ['back raised bed B', ['tomato-red beefsteak']],
            ['back raised bed C', ['romaine lettuce', 'kale', 'chard', 'beet']],
            ['back corner', ['avacado']],
            ['back patio', ['geranium', 'petunia']],
            ['side yard', ['potato-red', 'potato-golden','scallion', 'onion-white']],
            ['front yard', ['iris-purple', 'iris-white']],
        ]
    ],
    [
        '1225 SE 60th Ave, Portland, OR 97215',
        'calvin',
        'calvin',
        [
            ['greenhouse', ['tomato-cherry', 'tomato-cherokee purple', 'tomato-red beefsteak ', 'chili pepper-habenero', 'chili pepper-jalapeno', 'chili pepper-ghost pepper', 'chili pepper-serrano']],
            ['back covered garden', ['basil', 'cinnamon basil']],
            ['back yard', ['bell pepper-green', 'bell pepper-red', 'bell pepper-orange', 'bell pepper-yellow']],
            ['side yard', ['endive', 'romaine lettuce', 'kale']],
            ['front close in', ['spinach', 'arugula', 'marigold', 'petunia']],
            ['front streetside', ['avacado']],
            ['front middle', ['iris-purple', 'iris-white', 'iris-red']]
        ]
    ],
    [
        '5420 SE 41st Ave, Portland, OR 97202',
        'william',
        'william',
        [
            ['fron yard', [ 'chard', 'red cabbage', 'rhubarb', 'kale', 'romaine lettuce']],
            ['40th streetside', ['azalea']],
            ['corner', ['strawberry', 'raspberry', 'blackberry', 'marionberry']]
        ]
    ],
    [
        '1104 SE Nehalem St, Portland, OR 97202',
        'vern',
        'vern',
        [
            ['front yard', ['lavender', 'marigold', 'petunia']],
            ['back yard', ['potato-russet']],
            ['back corner', ['lavender', 'rosemary', 'thyme', 'basil']]
        ],
    ],
    [
        '5420 SE 41st Ave, Portland, OR 97202',
        'jm',
        'jm',
        [
            ['front streetside', ['apple-fuji', 'apple-honeycrisp', 'apple-granny smith']],
            ['back yard', ['avocado', 'tangerine', 'plum', 'peach']],
            ['back corner', ['sage', 'basil', 'rosemary', 'thai basil', 'thyme']]
        ]
    ],
    [
        '6010 SW Corbett Ave, Portland, OR 97239',
        'jan',
        'jan',
        [
            ['front yard', ['rose-red', 'rose-yellow', 'rose-white']],
            ['back yard', ['azalea', 'chard', 'kale', 'spinach', 'snow-peas', 'rhurbarb']],
            ['side yard', ['petunia']]
        ],
    ],
]

for ad in addresses:
    new_user = User(username=ad[1], email="{}@example.com".format(ad[1]))
    new_user.set_password(ad[2])
    session.add(new_user)
    print(new_user.username)
    address = ad[0]
    if address != '':
        response = requests.get('https://maps.googleapis.com/maps/api/geocode/json?address={}&key={}'.format(address, gkey))
        responseJSON = response.json()
        lat = responseJSON['results'][0]['geometry']['location']['lat']
        lon = responseJSON['results'][0]['geometry']['location']['lng']
        for g in ad[3]:
            new_garden = Garden(name=g[0], address=address, lat=lat, lon=lon)
            new_garden.users.append(new_user)
            session.add(new_garden)
            print("Garden Name:  ", new_garden.name, "    Grower:  ", new_user.username)
            for p in g[1]:
                new_plant = Plant(name=p, grower=new_user, garden=new_garden)
                session.add(new_plant)
                print(new_plant.name)
    post_body = random.choice(posts)
    post = Post(body=post_body, author=new_user)
    session.add(post)
session.commit()




print("-------------------------------------------------------------------")
print("-------------------------------------------------------------------")
print("-------------------------------------------------------------------")
print("-------------------------------------------------------------------")
print("Users, Gardens, Plants, and Posts added successfully!!!")
print("-------------------------------------------------------------------")
print("-------------------------------------------------------------------")
print("-------------------------------------------------------------------")
print("-------------------------------------------------------------------")
