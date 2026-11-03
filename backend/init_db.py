import pandas as pd
from sqlalchemy.orm import sessionmaker
from app.models.base import get_engine, Base
from app.models.anime import Anime
from app.models.rating import Rating
from app.models.genre import Genre

def seed_db():
    engine = get_engine()
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    print("Tables créées.")

if __name__ == '__main__' :
    seed_db()