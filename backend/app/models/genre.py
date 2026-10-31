from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.models.base import Base, BaseModelMixin
from app.models.association import anime_genre

class Genre(Base, BaseModelMixin):
    __tablename__ = 'genres'

    id = Column(Integer, primary_key=True, autoincrement=True)
    nom = Column(String(100), unique=True, nullable=False)

    animes = relationship("Anime", secondary=anime_genre, back_populates="genres")