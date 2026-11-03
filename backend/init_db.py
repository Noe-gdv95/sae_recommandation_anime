import pandas as pd
from sqlalchemy.orm import sessionmaker
from app.models.base import get_engine, Base
from app.models.anime import Anime
from app.models.rating import Rating

def seed_db():
    engine = get_engine()
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    print("Tables créées.")

    Session = sessionmaker(bind=engine)
    session = Session()

    print("Insertion des Animes en cours...")
    anime_df = pd.read_csv('../data/anime.csv')
    for _, row in anime_df.iterrows():
        anime = Anime(
            id=row['anime_id'], 
            nom=row['name'], 
            type=row['type'] if pd.notna(row['type']) else None,
            nb_episodes=row['episodes'] if 'episodes' in row and pd.notna(row['episodes']) else None,
            note_moyenne=row['rating'] if 'rating' in row and pd.notna(row['rating']) else None
        )
        session.add(anime)
    
    print("Insertion des Notes en cours...")
    rating_df = pd.read_csv('../data/rating.csv')
    notes_a_inserer = [
        Rating(
            user_id=r['user_id'], 
            anime_id=r['anime_id'], 
            rating=r['rating']
        )
        for _, r in rating_df.iterrows()
    ]

    session.bulk_save_objects(notes_a_inserer)
    session.commit()
    print("Succès ! Fichier de base de données créé et rempli.")

if __name__ == '__main__':
    seed_db()