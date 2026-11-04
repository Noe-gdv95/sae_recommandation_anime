from app.models.MesureDAO import MesureSqliteORM

class MesureService:
    def __init__(self):
        self.dao = MesureSqliteORM()

    def enregistrer(self, methode, anime_id, temps_ms, nb_resultats):
        self.dao.enregistrer(methode, anime_id, temps_ms, nb_resultats)

    def get_dernieres_mesures(self):
        return [m.to_dict() for m in self.dao.findDernieres()]

    def get_resume(self):
        resume = {}
        for methode, nb_appels, t_min, t_max, t_moyen in self.dao.resume_par_methode():
            resume[methode] = {
                "nb_appels": nb_appels,
                "temps_min_ms": round(t_min, 2) if t_min else 0,
                "temps_max_ms": round(t_max, 2) if t_max else 0,
                "temps_moyen_ms": round(t_moyen, 2) if t_moyen else 0,
            }
        return resume