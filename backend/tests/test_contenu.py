import unittest

from app.services.ContenuService import ContenuService, jaccard
from app.services.MesureService import centile, statistiques

ACTION, DRAME, FANTASTIQUE, COMEDIE, ROMANCE = 1, 2, 3, 4, 5

LIENS = [
    (10, ACTION), (10, DRAME), (10, FANTASTIQUE),
    (20, ACTION), (20, DRAME), (20, FANTASTIQUE),
    (30, ACTION), (30, FANTASTIQUE), (30, COMEDIE),
    (40, ACTION), (40, FANTASTIQUE), (40, ROMANCE),
    (50, COMEDIE), (50, ROMANCE),
    (60, DRAME),
]
INFOS = [
    (10, "TV", 1000), (20, "Movie", 50), (30, "Movie", 9000),
    (40, "TV", 10), (50, "TV", 99999), (60, "TV", 5),
]


def service_de_test():
    service = ContenuService(dao=object())
    service.charger_donnees(LIENS, INFOS)
    return service


class TestJaccard(unittest.TestCase):
    def test_valeurs(self):
        self.assertEqual(jaccard({1, 2, 3}, {1, 2, 3}), 1.0)
        self.assertEqual(jaccard({1, 2, 3}, {1, 3, 4}), 0.5)
        self.assertEqual(jaccard({1, 2}, {3, 4}), 0.0)
        self.assertEqual(jaccard(set(), {1}), 0.0)

    def test_symetrie(self):
        self.assertEqual(jaccard({1, 2}, {2, 3, 4}), jaccard({2, 3, 4}, {1, 2}))


class TestContenuService(unittest.TestCase):
    def setUp(self):
        self.service = service_de_test()

    def test_classement(self):
        recos = self.service.calculer(10, limite=10)
        self.assertEqual([a for a, _ in recos], [20, 40, 30, 60])
        self.assertAlmostEqual(dict(recos)[60], 1 / 3)

    def test_egalite_departagee_par_type_puis_popularite(self):
        recos = self.service.calculer(10, limite=10)
        self.assertLess([a for a, _ in recos].index(40), [a for a, _ in recos].index(30))

    def test_pas_de_soi_meme_ni_de_score_nul(self):
        ids = [a for a, _ in self.service.calculer(10, limite=10)]
        self.assertNotIn(10, ids)
        self.assertNotIn(50, ids)

    def test_limite(self):
        self.assertEqual(len(self.service.calculer(10, limite=2)), 2)

    def test_anime_inconnu(self):
        self.assertEqual(self.service.calculer(999), [])

    def test_index_identique_au_naif(self):
        for anime_id in self.service.genres_par_anime:
            self.assertEqual(self.service.scores_index(anime_id), self.service.scores_naif(anime_id))


class TestStatistiques(unittest.TestCase):
    def test_statistiques(self):
        stats = statistiques([4.0, 1.0, 3.0, 2.0, 100.0])
        self.assertEqual(stats["nb_appels"], 5)
        self.assertEqual(stats["temps_min_ms"], 1.0)
        self.assertEqual(stats["temps_max_ms"], 100.0)
        self.assertEqual(stats["temps_moyen_ms"], 22.0)
        self.assertEqual(stats["temps_median_ms"], 3.0)

    def test_centile(self):
        valeurs = list(range(1, 101))
        self.assertEqual(centile(valeurs, 95), 95)
        self.assertEqual(centile(valeurs, 50), 50)
        self.assertEqual(centile([7], 95), 7)


if __name__ == "__main__":
    unittest.main()
