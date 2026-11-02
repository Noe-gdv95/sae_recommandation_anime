from pathlib import Path
import pandas as pd

#Chemin du fichier CSV

DOSSIER_DATA = Path(__file__).resolve().parents[2] / "data"


def charger():
    anime = pd.read_csv(DOSSIER_DATA / "anime.csv")
    notes = pd.read_csv(DOSSIER_DATA / "rating.csv")
    print(f"anime.csv  : {len(anime)} lignes, colonnes {list(anime.columns)}")
    print(f"rating.csv : {len(notes)} lignes, colonnes {list(notes.columns)}")
    return anime, notes


if __name__ == "__main__":
    anime, notes = charger()