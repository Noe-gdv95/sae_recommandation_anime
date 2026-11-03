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

    Session = sessionmaker(bind=engine)
    session = Session()


    print ("Insertion des Animes en cours...")
    anime_df = pd.read_csv('../data/anime_propre.csv')
    for _, row in anime_df.iterrows():
        anime = Anime(
            anime_id=row['anime_id'], 
            name=row['name'], 
            type=row['type'] if pd.notna(row['type']) else None)
        session.add(anime)
    
    print("Insertion des Notes en cours...")
    rating_df = pd.read_csv('../data/rating_propre.csv')
    notes_a_inserer = [
        Rating(user_id=r['user_id'], anime_id=r['anime_id'], rating=r['rating'])
        for _, r in rating_df.iterrows()

    ]

    session.bulk_save_objects(notes_a_inserer)

    session.commit()
    print("Succès ! Fichier de base de données créé et rempli.")

if __name__ == '__main__' :
    seed_db()