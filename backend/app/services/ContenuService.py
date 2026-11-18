"""
Méthode 1 : recommandation basée sur le contenu (indice de Jaccard sur les genres).

Idée : deux anime se ressemblent s'ils partagent beaucoup de genres.
On compare l'ensemble des genres de l'anime choisi (A) avec celui de chaque
autre anime (B) grâce à l'indice de Jaccard :

    J(A, B) = |A ∩ B| / |A ∪ B| = |A ∩ B| / (|A| + |B| - |A ∩ B|)

- J = 1 : exactement les mêmes genres.
- J = 0 : aucun genre en commun.

Exemple : A = {Action, Drame, Fantastique}, B = {Action, Fantastique, Comédie}
    A ∩ B = {Action, Fantastique}                 -> 2 genres
    A ∪ B = {Action, Drame, Fantastique, Comédie} -> 4 genres
    J(A, B) = 2 / 4 = 0,5

Notations pour la complexité :
    N  = nombre d'anime (≈ 11 000 après nettoyage)
    g  = nombre moyen de genres par anime (≈ 3)
    gA = nombre de genres de l'anime choisi
    C  = nombre de candidats, c.-à-d. d'anime qui partagent au moins un genre avec A

Deux versions sont codées pour pouvoir les comparer (rapport d'optimisation) :

1. Version naïve (`scores_naif`) : on calcule J(A, B) pour les N anime.
   Coût : O(N · g).

2. Version avec index inversé (`scores_index`), utilisée par défaut.
   L'index inversé associe à chaque genre la liste des anime qui l'ont :
       index[Action] = [1, 5, 20, ...]
   En parcourant uniquement les listes des genres de A, on compte |A ∩ B|
   pour chaque B qui partage au moins un genre. Les anime sans genre commun
   (J = 0) ne sont jamais visités.
   Coût : O(C · gA) au pire.

Ensuite, les candidats sont triés par score : O(C · log C).

Le chargement des données (base -> mémoire) est fait une seule fois, au premier
appel : O(N · g). Les appels suivants n'interrogent plus la base que pour
récupérer les anime à afficher.
"""
from typing import Dict, List, Set, Tuple

from app.models.AnimeDAO import AnimeSqliteORM


def jaccard(genres_a: Set[int], genres_b: Set[int]) -> float:
    """Indice de Jaccard entre deux ensembles de genres (valeur entre 0 et 1)."""
    if len(genres_a) == 0 or len(genres_b) == 0:
        return 0.0
    intersection = len(genres_a & genres_b)
    union = len(genres_a) + len(genres_b) - intersection
    return intersection / union


class ContenuService:
    METHODE = "contenu"

    def __init__(self, dao=None):
        if dao is None:
            dao = AnimeSqliteORM()
        self.dao = dao
        self.genres_par_anime: Dict[int, Set[int]] = {}   # {anime_id: {genre_id, ...}}
        self.index_inverse: Dict[int, List[int]] = {}     # {genre_id: [anime_id, ...]}
        self.type_par_anime: Dict[int, str] = {}          # {anime_id: "TV" / "Movie" / ...}
        self.membres_par_anime: Dict[int, int] = {}       # {anime_id: nb_membres}
        self.donnees_chargees = False

    # ------------------------------------------------------------------
    # Chargement des données en mémoire (une seule fois)
    # ------------------------------------------------------------------
    def charger_donnees(self, liens_anime_genre, infos_animes) -> None:
        """
        Construit les structures utilisées par l'algorithme.

        liens_anime_genre : liste de paires (anime_id, genre_id)
        infos_animes      : liste de triplets (anime_id, type, nb_membres)
        """
        self.genres_par_anime = {}
        self.index_inverse = {}
        for anime_id, genre_id in liens_anime_genre:
            self.genres_par_anime.setdefault(anime_id, set()).add(genre_id)
            self.index_inverse.setdefault(genre_id, []).append(anime_id)

        self.type_par_anime = {}
        self.membres_par_anime = {}
        for anime_id, type_anime, nb_membres in infos_animes:
            self.type_par_anime[anime_id] = type_anime
            self.membres_par_anime[anime_id] = nb_membres or 0

        self.donnees_chargees = True

    def charger_si_besoin(self) -> None:
        if not self.donnees_chargees:
            self.charger_donnees(self.dao.findLiensAnimeGenre(), self.dao.findInfosAnimes())

    # ------------------------------------------------------------------
    # Calcul des scores
    # ------------------------------------------------------------------
    def scores_naif(self, anime_id: int) -> Dict[int, float]:
        """Version naïve : Jaccard contre tous les anime. O(N · g)."""
        genres_a = self.genres_par_anime[anime_id]
        scores = {}
        for autre_id, genres_b in self.genres_par_anime.items():
            if autre_id == anime_id:
                continue
            score = jaccard(genres_a, genres_b)
            if score > 0:
                scores[autre_id] = score
        return scores

    def scores_index(self, anime_id: int) -> Dict[int, float]:
        """Version optimisée : seuls les anime partageant un genre sont visités."""
        genres_a = self.genres_par_anime[anime_id]

        # 1. Compter |A ∩ B| pour chaque candidat B grâce à l'index inversé
        intersections = {}
        for genre_id in genres_a:
            for autre_id in self.index_inverse[genre_id]:
                intersections[autre_id] = intersections.get(autre_id, 0) + 1
        intersections.pop(anime_id, None)  # on ne se recommande pas soi-même

        # 2. En déduire Jaccard sans calculer l'union : |A ∪ B| = |A| + |B| - |A ∩ B|
        taille_a = len(genres_a)
        scores = {}
        for autre_id, inter in intersections.items():
            taille_b = len(self.genres_par_anime[autre_id])
            scores[autre_id] = inter / (taille_a + taille_b - inter)
        return scores

    def calculer(self, anime_id: int, limite: int = 10, naif: bool = False) -> List[Tuple[int, float]]:
        """
        Renvoie les `limite` meilleurs anime sous forme de liste [(anime_id, score), ...],
        du plus similaire au moins similaire. Liste vide si l'anime n'a pas de genre connu.

        En cas d'égalité de score (fréquent : il n'y a que 42 genres), on départage :
          1. d'abord les anime du même type (série, film...) que l'anime choisi ;
          2. puis les plus populaires (nombre de membres MyAnimeList).
        """
        self.charger_si_besoin()
        if anime_id not in self.genres_par_anime:
            return []

        if naif:
            scores = self.scores_naif(anime_id)
        else:
            scores = self.scores_index(anime_id)

        type_a = self.type_par_anime.get(anime_id)

        def cle_de_tri(item):
            autre_id, score = item
            meme_type = self.type_par_anime.get(autre_id) == type_a
            return (score, meme_type, self.membres_par_anime.get(autre_id, 0))

        classement = sorted(scores.items(), key=cle_de_tri, reverse=True)
        return classement[:limite]

    # ------------------------------------------------------------------
    # Point d'entrée utilisé par le controller
    # ------------------------------------------------------------------
    def recommander(self, anime_id: int, limite: int = 10) -> List[Dict]:
        """
        Recommandations prêtes à afficher :
        [{"anime": Anime, "score": 0.75, "genres_communs": ["Action", ...]}, ...]
        """
        meilleurs = self.calculer(anime_id, limite)
        if len(meilleurs) == 0:
            return []

        ids = [anime_id] + [autre_id for autre_id, _ in meilleurs]
        animes = self.dao.findByIds(ids)
        genres_choisi = {genre.nom for genre in animes[anime_id].genres}

        resultats = []
        for autre_id, score in meilleurs:
            anime = animes.get(autre_id)
            if anime is None:
                continue
            genres_autre = {genre.nom for genre in anime.genres}
            resultats.append({
                "anime": anime,
                "score": round(score, 4),
                "genres_communs": sorted(genres_choisi & genres_autre),
            })
        return resultats
