from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from app import create_app, db
from app.models import User, Plant, Garden, Post
import random

app = create_app()
app_context = app.app_context()
app_context.push()

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


posts = [
    'Hello!', 'How are you people doing?', 'How is everybody doing?', 'hello', 'hello!', 'Hello',
    'I just planted something!', "What's the weather like for everybod?", 'Happy planting!', "What's going on in the neighborhood?",
    'mmmm tomatoes', 'alright', "It's so nice outside today", "I'm back baby", "yarp", "narp"
]

users = [
    'aya', 'gb', 'gregor', 'gregorius', 'bob', 'hamburgler', 'cornelius',
    'wilhelm', 'merwin', 'edmund', 'munster', 'wilbur', 'susan', 'harold', 'jon',
    'john', 'jeff', 'richard', 'evan', 'ethan', 'alvin', 'calvin', 'william',
    'vern', 'jm', 'jan'
]

for u in users:
    user = User.query.filter_by(username=u).first_or_404()
    for x in range(7):
        recipient_name = random.choice(users)
        print(recipient_name)
        recipient = User.query.filter_by(username=recipient_name).first_or_404()
        if user.username == recipient_name:
            wall_post = Post(body="I'm posting on my own wall. Oops!", author=user, wall_post=True, wall_owner_id=recipient.id)
        else:
            wall_post = Post(body="Hello {}".format(recipient_name), author=user, wall_post=True, wall_owner_id=recipient.id)
            user.follow(recipient)
        db.session.add(wall_post)
db.session.commit()

print('-------------------------------')
print('-------------------------------')
print('-------------------------------')
print('-------------------------------')
print('-------------------------------')
print('Wall Posts added successfull!!!')
print('-------------------------------')
print('-------------------------------')
print('-------------------------------')
print('-------------------------------')
print('-------------------------------')
