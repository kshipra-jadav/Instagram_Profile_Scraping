from db.engine import engine
from db.base import Base

def init_db():
    Base.metadata.create_all(engine)
