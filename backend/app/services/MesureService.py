from app.models.MesureDAO import MesureSqliteORM

class MesureService:
    def __init__(self):
        self.dao = MesureSqliteORM()

    def enregistrer(self, methode, anime_id, temps_ms, nb_resultats):
        self.dao.enregistrer(methode, anime_id, temps_ms, nb_resultats)

    def get_dernieres_mesures(self):
        return [m.to_dict() for m in self.dao.findDernieres()]