from db.engine import engine
from db.base import Base
from db.influencer import Influencer  

def init_db():
    Base.metadata.create_all(engine)
