# Recommandation d'anime : 
Application web qui recommande des anime à partir d'un anime choisi,
et chronomètre chaque recommandation pour comparer les méthodes.

- **Backend** : API Flask (Python) qui renvoie du JSON, SQLAlchemy et SQLite
- **Frontend** : HTML, CSS et JavaScript, avec Chart.js pour les graphiques
- **Données** : [Anime Recommendations Database](https://www.kaggle.com/datasets/CooperUnion/anime-recommendations-database) (Kaggle)

## Équipe
- Baskara Steven : nettoyage et import des données
- Goncalves De Veiga Noé : API et base de données
- Diakité Badjiry : frontend
- Bouciouf Tallal : algorithme de recommandation

## Installation

### 1. Télécharger les données
Le dataset n'est pas dans le dépôt (trop lourd).
1. Télécharger le dataset sur Kaggle (lien ci-dessus).
2. Créer un dossier `data/` à la racine du projet.
3. Y placer `anime.csv` et `rating.csv`.

```
sae_recommandation_anime/
├── data/
│   ├── anime.csv
│   └── rating.csv
├── backend/
└── frontend/
```

### 2. Créer l'environnement Python
Depuis la racine du projet :
```bash
python -m venv venv
```
- Windows : `.\venv\Scripts\activate`
- Linux / macOS : `source venv/bin/activate`

```bash
pip install -r requirements.txt
```

### 3. Nettoyer les données et remplir la base
Depuis la racine du projet :
```bash
python backend/scripts/nettoyage_donnees.py
cd backend
python init_db.py
```
Le nettoyage crée `data/anime_propre.csv` et `data/rating_propre.csv`
(il retire les notes à -1, les contenus pour adultes et les doublons).
`init_db.py` crée `backend/anime_reco.db` .

## Lancement

**Terminal 1 : l'API** (depuis `backend/`, avec le venv activé)
```bash
python main.py
```
L'API tourne sur http://localhost:8000

**Terminal 2 : le site** (depuis `frontend/`)
```bash
python -m http.server 5500
```
Ouvrir http://localhost:5500

