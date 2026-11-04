import time
from pathlib import Path

import pandas as pd
from sqlalchemy import insert
from sqlalchemy.orm import sessionmaker

from app.models.base import get_engine, Base
from app.models.anime import Anime
from app.models.genre import Genre
from app.models.rating import Rating
from app.models.association import anime_genre

DOSSIER_DATA = Path(__file__).resolve().parents[1] / "data"

def creer_tables(engine):
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    print("Tables créées.")

def valeur(x):
    if pd.isna(x):
        return None 
    return x

def inserer_animes(session, anime_df):
    lignes = []
    for anime in anime_df.itertuples(index=False):
        lignes.append({
            "id" : int(anime.anime_id),
            "nom" : anime.name,
            "type" : valeur(anime.type),
            "nb_episodes" : None if pd.isna(anime.episodes) else int(anime.episodes),
            "note_moyenne" : valeur(anime.rating),
            "nb_membres" : int(anime.members),

        })
    session.execute(insert(Anime), lignes)
    print(f"Anime insérés : {len(lignes)}")