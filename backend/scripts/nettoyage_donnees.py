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



def nettoyer_anime(anime):
    print("\n--- Nettoyage de anime.csv ---")
    depart = len(anime)

    anime = anime.drop_duplicates(subset="anime_id")
    print(f"Doublons d'identifiant retirés : {depart - len(anime)}")

    anime["genre"] = anime["genre"].apply(nettoyer_genres)

    avant = len(anime)
    anime = anime.dropna(subset=["genre"])
    print(f"Anime sans genre retirés : {avant - len(anime)}")

    avant = len(anime)
    adulte = anime["genre"].str.contains("Hentai")
    anime = anime[~adulte]
    print(f"Contenus pour adultes retirés : {avant - len(anime)}")

    anime["name"] = anime["name"].apply(html.unescape).str.strip()

    inconnus = (anime["episodes"] == "Unknown").sum()
    anime["episodes"] = pd.to_numeric(anime["episodes"], errors="coerce").astype("Int64")
    print(f"Nombres d'épisodes inconnus (gardés vides) : {inconnus}")

    print(f"Types manquants (gardés vides) : {anime['type'].isna().sum()}")
    print(f"Notes moyennes manquantes (gardées vides) : {anime['rating'].isna().sum()}")

    print(f"=> {len(anime)} anime gardés sur {depart}")

    return anime



def nettoyer_notes(notes, ids_anime):
    print("\n--- Nettoyage de rating.csv ---")
    depart = len(notes)

    avant = len(notes)
    notes = notes[notes["rating"] != -1]
    print(f"Notes à -1 retirées : {avant - len(notes)}")

    avant = len(notes)
    notes = notes[notes["anime_id"].isin(ids_anime)]
    print(f"Notes d'anime retirés ou inconnus : {avant - len(notes)}")

    avant = len(notes)
    notes = notes.drop_duplicates(subset=["user_id", "anime_id"], keep="last")
    print(f"Doublons utilisateur/anime retirés : {avant - len(notes)}")

    print(f"=> {len(notes)} notes gardées sur {depart}")
    return notes



if __name__ == "__main__":
    anime, notes = charger()
    anime = nettoyer_anime(anime)
    notes = nettoyer_notes(notes, set(anime["anime_id"]))