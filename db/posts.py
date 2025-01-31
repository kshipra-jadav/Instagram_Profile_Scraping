from sqlalchemy import Column, String, Integer, BigInteger, ARRAY, ForeignKey
from sqlalchemy.orm import relationship

from db.base import Base

class Posts(Base):
    __tablename__ = "Posts"

    user_id = Column(String(50), ForeignKey('Influencer.instagram_id'), primary_key=False)
    short_code = Column(String(100), primary_key=True)
    image_url = Column(String(5000), nullable=False)
    tagged_users = Column(ARRAY(String), nullable=True)
    sponsored_users = Column(ARRAY(String), nullable=True)
    caption = Column(String(1000), nullable=True)
    num_comments = Column(Integer, nullable=False)
    num_likes = Column(BigInteger, nullable=False)
    timestamp = Column(BigInteger, nullable=False)

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
