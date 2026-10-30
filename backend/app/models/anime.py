from sqlalchemy import Column, Integer, String, Float
from app.models.base import Base, BaseModelMixin

class Anime(Base, BaseModelMixin):
    __tablename__ = 'animes'

    id = Column(Integer, primary_key=True)
    nom = Column(String(255), nullable=False, index=True)
    type = Column(String(50), nullable=False)
    nb_episodes = Column(Integer, nullable=True)
    note_moyenne = Column(Float, nullable=True)
    nb_membres = Column(Integer, nullable=True)