
import sqlalchemy

from sqlalchemy import *
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

Base = declarative_base()

engine = create_engine("postgresql://admin:QoiO7D-xmmzcCOxTWup6xjIicWoNFb@ap-south-1.5e98aaa0-7d64-4a7e-80eb-5c3923368534.aws.yugabyte.cloud:5433/yugabyte")

Session = sessionmaker(bind = engine)
session = Session()

# querying 'influencers' table

influencers_data = session.query(Influencers).all()

# Influencers: class name defined previously, no need for that code to be here again, i.e., 
# this class name exists independently now in the database as an association 
# (even though it is not the table name! Due to a data sample/row of that table being an object and 
# belonging to that class)

for influencer in influencers_data:
    print(influencer)

print('')

# querying 'posts' table

posts_data = session.query(Posts).all()

# Posts: class name defined previously

for post in posts_data:
    print(post)

print('')

session.close()
engine.dispose()


