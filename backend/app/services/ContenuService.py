from typing import Dict, List, Set, Tuple

from app.models.AnimeDAO import AnimeSqliteORM


def jaccard(genres_a: Set[int], genres_b: Set[int]) -> float:
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
        self.genres_par_anime: Dict[int, Set[int]] = {}
        self.index_inverse: Dict[int, List[int]] = {}
        self.type_par_anime: Dict[int, str] = {}
        self.membres_par_anime: Dict[int, int] = {}
        self.donnees_chargees = False

    def charger_donnees(self, liens_anime_genre, infos_animes) -> None:
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

    def scores_naif(self, anime_id: int) -> Dict[int, float]:
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
        genres_a = self.genres_par_anime[anime_id]

        intersections = {}
        for genre_id in genres_a:
            for autre_id in self.index_inverse[genre_id]:
                intersections[autre_id] = intersections.get(autre_id, 0) + 1
        intersections.pop(anime_id, None)

        taille_a = len(genres_a)
        scores = {}
        for autre_id, inter in intersections.items():
            taille_b = len(self.genres_par_anime[autre_id])
            scores[autre_id] = inter / (taille_a + taille_b - inter)
        return scores

    def calculer(self, anime_id: int, limite: int = 10, naif: bool = False) -> List[Tuple[int, float]]:
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

    def recommander(self, anime_id: int, limite: int = 10) -> List[Dict]:
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
