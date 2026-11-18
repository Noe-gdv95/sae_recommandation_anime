"""
Service de mesure des performances des méthodes de recommandation.

- `chronometrer` exécute une méthode de recommandation, mesure son temps
  d'exécution avec time.perf_counter() (horloge précise, non affectée par
  un changement de l'heure du système) et enregistre la mesure en base.
- `get_resume` calcule, pour chaque méthode, les statistiques affichées
  dans le tableau de bord : min, max, moyenne, médiane, écart-type et
  95e centile (p95 : 95 % des appels sont plus rapides que cette valeur).

La médiane et le p95 sont moins sensibles que la moyenne aux valeurs extrêmes,
par exemple le premier appel qui charge les données en mémoire.
"""
import math
import time
from typing import Dict, List

from app.models.MesureDAO import MesureSqliteORM


def moyenne(valeurs: List[float]) -> float:
    return sum(valeurs) / len(valeurs)


def mediane(valeurs_triees: List[float]) -> float:
    """Valeur du milieu (moyenne des deux du milieu si le nombre de valeurs est pair)."""
    n = len(valeurs_triees)
    milieu = n // 2
    if n % 2 == 1:
        return valeurs_triees[milieu]
    return (valeurs_triees[milieu - 1] + valeurs_triees[milieu]) / 2


def ecart_type(valeurs: List[float]) -> float:
    """Racine de la moyenne des carrés des écarts à la moyenne."""
    m = moyenne(valeurs)
    variance = sum((v - m) ** 2 for v in valeurs) / len(valeurs)
    return math.sqrt(variance)


def centile(valeurs_triees: List[float], p: float) -> float:
    """Centile p (entre 0 et 100) : la valeur au rang ceil(p/100 × n) dans la liste triée."""
    if len(valeurs_triees) == 0:
        return 0
    rang = math.ceil(p / 100 * len(valeurs_triees))
    rang = max(rang, 1)
    return valeurs_triees[rang - 1]


def statistiques(temps: List[float]) -> Dict:
    """Statistiques d'une liste de temps (en ms). Le tri coûte O(M log M)."""
    tries = sorted(temps)
    return {
        "nb_appels": len(tries),
        "temps_min_ms": round(tries[0], 2),
        "temps_max_ms": round(tries[-1], 2),
        "temps_moyen_ms": round(moyenne(tries), 2),
        "temps_median_ms": round(mediane(tries), 2),
        "ecart_type_ms": round(ecart_type(tries), 2),
        "temps_p95_ms": round(centile(tries, 95), 2),
    }


class MesureService:
    def __init__(self):
        self.dao = MesureSqliteORM()

    def chronometrer(self, methode: str, anime_id: int, fonction, *args, **kwargs):
        """
        Appelle fonction(*args, **kwargs), mesure son temps d'exécution et l'enregistre.
        Renvoie (resultats, temps_ms). L'écriture en base est faite après l'arrêt
        du chronomètre : elle n'est pas comptée dans le temps de la méthode.
        """
        debut = time.perf_counter()
        resultats = fonction(*args, **kwargs)
        temps_ms = (time.perf_counter() - debut) * 1000
        self.enregistrer(methode, anime_id, temps_ms, len(resultats))
        return resultats, temps_ms

    def enregistrer(self, methode: str, anime_id: int, temps_ms: float, nb_resultats: int) -> None:
        self.dao.enregistrer(methode, anime_id, temps_ms, nb_resultats)

    def get_dernieres_mesures(self) -> List[Dict]:
        return [m.to_dict() for m in self.dao.findDernieres()]

    def get_resume(self) -> Dict[str, Dict]:
        temps_par_methode = {}
        for methode, temps_ms in self.dao.findTempsParMethode():
            temps_par_methode.setdefault(methode, []).append(temps_ms)

        resume = {}
        for methode, temps in temps_par_methode.items():
            resume[methode] = statistiques(temps)
        return resume
