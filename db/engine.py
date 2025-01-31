from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


HOST = "ap-south-1.5e98aaa0-7d64-4a7e-80eb-5c3923368534.aws.yugabyte.cloud"
USERNAME = "admin"
PASSWORD = "QoiO7D-xmmzcCOxTWup6xjIicWoNFb"
PORT = 5433
DBNAME = 'yugabyte'

DB_URL = f"postgresql://{USERNAME}:{PASSWORD}@{HOST}:{PORT}/{DBNAME}"

engine = create_engine(DB_URL)

def make_session():

    Session = sessionmaker(bind=engine)

    session = Session()

    return session