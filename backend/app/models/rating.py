from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import Base, BaseModelMixin

class Rating(Base, BaseModelMixin):
    __tablename__ = 'ratings'

    id = Column(Integer,primary_key=True, autoincrement=True)
    user_id = Column(Integer,nullable=False, index=True)
    anime_id = Column(Integer,ForeignKey('animes.id', ondelete='CASCADE'), nullable=False)
    rating = Column(Integer, nullable=False)

    anime = relationship("Anime", back_populates="ratings")