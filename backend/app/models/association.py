from sqlalchemy import Table, Column, Integer, ForeignKey
from app.models.base import Base

anime_genre = Table(
    'anime_genre',
    Base.metadata,
    Column('anime_id', Integer, ForeignKey('animes.id', ondelete='CASCADE'), primary_key=True),
    Column('genre_id', Integer, ForeignKey('genres.id', ondelete='CASCADE'), primary_key=True)
)