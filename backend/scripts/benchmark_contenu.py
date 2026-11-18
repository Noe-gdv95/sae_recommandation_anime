"""
Benchmark de la Méthode 1 (Jaccard) : version naïve contre version avec index inversé.

Lancement depuis backend/ (base déjà remplie) :
    python -m scripts.benchmark_contenu
"""
import random
import time

from app.services.ContenuService import ContenuService
from app.services.MesureService import statistiques

NB_ANIME_TESTES = 300
NB_REPETITIONS = 5


def chrono_ms(fonction, *args, **kwargs) -> float:
    debut = time.perf_counter()
    fonction(*args, **kwargs)
    return (time.perf_counter() - debut) * 1000


def main():
    service = ContenuService()
    temps_chargement = chrono_ms(service.charger_si_besoin)

    ids = list(service.genres_par_anime)
    random.seed(42)  # même échantillon à chaque lancement
    echantillon = random.sample(ids, min(NB_ANIME_TESTES, len(ids)))

    total_candidats = 0
    for anime_id in echantillon:
        total_candidats += len(service.scores_index(anime_id))

    print(f"Anime en mémoire : {len(ids)}  |  genres : {len(service.index_inverse)}")
    print(f"Chargement initial (base -> mémoire) : {temps_chargement:.1f} ms")
    print(f"Candidats visités par l'index (moyenne) : {total_candidats / len(echantillon):.0f} sur {len(ids) - 1}")
    print()

    for nom, naif in (("naïve", True), ("index inversé", False)):
        temps = []
        for _ in range(NB_REPETITIONS):
            for anime_id in echantillon:
                temps.append(chrono_ms(service.calculer, anime_id, 10, naif=naif))
        s = statistiques(temps)
        print(f"Version {nom:<14} min {s['temps_min_ms']:6.2f} ms | médiane {s['temps_median_ms']:6.2f} ms"
              f" | moyenne {s['temps_moyen_ms']:6.2f} ms | max {s['temps_max_ms']:6.2f} ms")

    # Vérification : les deux versions donnent les mêmes recommandations
    differences = 0
    for anime_id in echantillon:
        if service.calculer(anime_id, 10, naif=True) != service.calculer(anime_id, 10):
            differences += 1
    print(f"\nRésultats différents entre les deux versions : {differences}")


if __name__ == "__main__":
    main()
