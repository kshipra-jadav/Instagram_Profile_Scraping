from sqlalchemy import Column, String, Integer, BigInteger, ARRAY

from db.base import Base

class Influencer(Base):
    __tablename__ = "Influencer"

    instagram_id = Column(String(50), primary_key=True)
    name = Column(String(255), nullable=False)
    category = Column(String(50), nullable=True)
    enum = Column(String(50), nullable=True)
    num_posts = Column(Integer, nullable=False)
    num_followers = Column(BigInteger, nullable=False)
    biography = Column(String(5000), nullable=False)
    related_profiles = Column(ARRAY(String), nullable=False)

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def __repr__(self):
        return (f"Influencer({self.instagram_id}, {self.name}, {self.category}, "
                f"{self.num_posts}, {self.num_followers}, {self.related_profiles}, {self.biography})")