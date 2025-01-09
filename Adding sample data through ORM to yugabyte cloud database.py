
import sqlalchemy

from sqlalchemy import *
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

Base = declarative_base()

# creating Python classes for database tables

class Influencers(Base):
    __tablename__ = 'influencers'
    
    influencer_id = Column(String(50), primary_key = True)  # primary key
    full_name = Column(String(255), nullable = False)  # String here: In SQL, corresponds to VARCHAR
    category_name = Column(String(255))     # default: nullable = True
    num_of_posts = Column(Integer, nullable = False)
    num_of_followers = Column(BigInteger, nullable = False)
    bio = Column(String(255))
    
    def __init__(self, influencer_id = None, full_name = None, category_name = None, 
                 num_of_posts = None, num_of_followers = None, bio = None):
        self.influencer_id = influencer_id
        self.full_name = full_name
        self.category_name = category_name
        self.num_of_posts = num_of_posts
        self.num_of_followers = num_of_followers
        self.bio = bio
        
    def __repr__(self):
        return f'Influencer({self.influencer_id}, {self.full_name}, {self.category_name}, {self.num_of_posts}, {self.num_of_followers}, {self.bio})'
    
    # Relationship to posts
    
    posts = relationship('Posts', back_populates = 'influencers')
            

class Posts(Base):
    __tablename__ = 'posts'
    
    influencer_id = Column(String(50), ForeignKey('influencers.influencer_id'), nullable = False)  # foreign key to main table 'influencers'
    
    post_short_code = Column(String(50), primary_key = True) # primary key
    image_url = Column(String(5000))
    caption = Column(String(5000))
    num_of_likes = Column(BigInteger, nullable = False)
    num_of_comments = Column(Integer, nullable = False)
    time_stamp = Column(BigInteger, nullable = False)

    
    def __init__(self, influencer_id = None, post_short_code = None, image_url = None, 
                 caption = None, num_of_likes = None, num_of_comments = None, time_stamp = None):
        self.influencer_id = influencer_id
        self.post_short_code = post_short_code
        self.image_url = image_url
        self.caption = caption
        self.num_of_likes = num_of_likes
        self.num_of_comments = num_of_comments
        self.time_stamp = time_stamp
        
    def __repr__(self):
        return f'Post({self.influencer_id}, {self.post_short_code}, {self.image_url}, {self.caption}, {self.num_of_likes}, {self.num_of_comments}, {self.time_stamp})'
    
    # Relationship to influencers
    
    influencers = relationship('Influencers', back_populates = 'posts')


# using YugabyteDB as the cloud-based SQL (Structured Query Language) database
# (specifically, YugabyteDB Aeon)

# engine = create_engine("postgresql://user_name (default username: admin):YSQL_password@cluster_host:YSQL_port/database_name (default database name: yugabyte)")

# 5433: default port for YSQL

engine = create_engine("postgresql://admin:QoiO7D-xmmzcCOxTWup6xjIicWoNFb@ap-south-1.5e98aaa0-7d64-4a7e-80eb-5c3923368534.aws.yugabyte.cloud:5433/yugabyte")
Base.metadata.create_all(engine)

# sample data insertion

## creating session:

Session = sessionmaker(bind = engine)
session = Session()

## sample:

# adding data to 'Influencers' table    

influ_1 = Influencers("173560420", "Cristiano Ronaldo", "Athlete", 3813, 647045617, "SIUUUbscribe to my Youtube Channel!")

try:
    session.add(influ_1)
    
    # the classes to which the objects being added to the session belong to, automatically determine 
    # which table the data will be inserted into
    # The table name is implicitly tied to the Python class defined with Base
    # Each table is tied to a class with the __tablename__ attribute
    
    session.commit()
    print('Your data has been inserted successfully')
    print('')
except Exception as e:
    session.rollback()
    print('The following error has occurred: ', e)
    print('')
finally:
    session.close()
    
# adding data to 'Posts' table

## creating session:

session = Session()

# querying (extracting) the object (to dynamically get its 'influencer_id' field and utilise it in adding data to 'posts' table):-

influ_1_from_db = session.query(Influencers).filter_by(full_name = "Cristiano Ronaldo")
# can also be queried by using other fields of 'influencers' table

# Influencers: class name

# getting influncer 1's id

influ_1_id = influ_1_from_db.influencer_id

post_influ_1 = Posts(influ_1_id, "DCH5pwtAM9m", "https://scontent-bom2-3.cdninstagram.com/v/t51.2885-15/466368384_18586973194056421_1214862776315273182_n.jpg?stp=dst-jpg_e35_s1080x1080_sh0.08_tt6&_nc_ht=scontent-bom2-3.cdninstagram.com&_nc_cat=101&_nc_ohc=8I-m13TQr5wQ7kNvgGR1kJo&_nc_gid=27b18d35744b4edf9214af41f48fd157&edm=APU89FABAAAA&ccb=7-5&oh=00_AYCjn5wMIvlGKh-o9tjj6_wecrPMhLtb2Qtm8eoB0LYAdQ&oe=678418E2&_nc_sid=bc0c2c", "Victory fuels our rise", 5817726, 26695, 1731096956)

try:
    session.add(post_influ_1)
    session.commit()
    print('Your data has been inserted successfully')
    print('')
except Exception as e:
    session.rollback()
    print('The following error has occurred: ', e)
    print('')
finally:
    session.close()
    engine.dispose()

