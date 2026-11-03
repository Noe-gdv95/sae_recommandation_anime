from sqlalchemy import Column, Integer, String, Float
from app.models.base import Base, BaseModelMixin
from sqlalchemy.orm import relationship
from app.models.association import anime_genre


class Anime(Base, BaseModelMixin):
    __tablename__ = 'animes'

    id = Column(Integer, primary_key=True)
    nom = Column(String(255), nullable=False, index=True)
    type = Column(String(50), nullable=True)
    nb_episodes = Column(Integer, nullable=True)
    note_moyenne = Column(Float, nullable=True)
    nb_membres = Column(Integer, nullable=True)

    genres = relationship("Genre", secondary=anime_genre, back_populates="animes")
    ratings = relationship("Rating", back_populates="anime", cascade="all, delete-orphan")