from sqlalchemy import Column
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass

class Influencer(Base):
    __tablename__ = "Influencer"


