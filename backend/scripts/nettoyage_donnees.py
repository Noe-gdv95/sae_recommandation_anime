import html
from pathlib import Path

import pandas as pd

# Chemin du dossier data 

DOSSIER_DATA = Path(__file__).resolve().parents[2] / "data"


def charger():
    anime = pd.read_csv(DOSSIER_DATA / "anime.csv")
    notes = pd.read_csv(DOSSIER_DATA / "rating.csv")
    print(f"anime.csv  : {len(anime)} lignes, colonnes {list(anime.columns)}")
    print(f"rating.csv : {len(notes)} lignes, colonnes {list(notes.columns)}")
    return anime, notes


def nettoyer_genres(texte):
    if pd.isna(texte):
        return None

    morceaux = texte.split(",")

    genres = []
    for morceau in morceaux:
        genre = morceau.strip()
        if genre != "":
            genres.append(genre)

    genres = list(dict.fromkeys(genres))

    if len(genres) == 0:
        return None
    return ", ".join(genres)


if __name__ == "__main__":
    print(nettoyer_genres("Comedy, Sci-Fi, Shounen, Shounen"))
    print(nettoyer_genres("  Action ,Drama"))
    print(nettoyer_genres(None))