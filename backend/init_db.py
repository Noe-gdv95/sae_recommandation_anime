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
            "id": int(anime.anime_id),
            "nom": anime.name,
            "type": valeur(anime.type),
            "nb_episodes": None if pd.isna(anime.episodes) else int(anime.episodes),
            "note_moyenne": valeur(anime.rating),
            "nb_membres": int(anime.members),
        })
    session.execute(insert(Anime), lignes)
    print(f"Anime insérés : {len(lignes)}")


def inserer_genres(session, anime_df):
    tous_les_genres = set()
    for texte in anime_df["genre"]:
        if pd.notna(texte):
            for genre in str(texte).split(", "):
                tous_les_genres.add(genre)

    id_par_genre = {}
    for numero, nom in enumerate(sorted(tous_les_genres), start=1):
        id_par_genre[nom] = numero
    session.execute(insert(Genre), [{"id": i, "nom": nom} for nom, i in id_par_genre.items()])

    liens = []
    for anime_id, texte in zip(anime_df["anime_id"], anime_df["genre"]):
        if pd.notna(texte):
            for genre in str(texte).split(", "):
                liens.append({"anime_id": int(anime_id), "genre_id": id_par_genre[genre]})
    session.execute(insert(anime_genre), liens)
    print(f"Genres insérés : {len(id_par_genre)}, liens anime-genre : {len(liens)}")

def inserer_notes(session, rating_df, taille_paquet=100_000):
    for debut in range(0, len(rating_df), taille_paquet):
        paquet = rating_df.iloc[debut:debut + taille_paquet]
        session.execute(inserert(Rating), paquet.to_dict("records"))
    print(f"Notes insérées : {len(rating_df)}")