from sqlalchemy import func
from sqlalchemy.orm import sessionmaker
from app.models.base import get_engine
from app.models.mesure import Mesure

class MesureSqliteORM:
    def __init__(self, db_uri=None):
        self.engine = get_engine(db_uri)
        self.SessionFactory = sessionmaker(bind=self.engine, expire_on_commit=False)

    def connect(self):
        return self.SessionFactory()

    def enregistrer(self, methode, anime_id, temps_ms, nb_resultats):
        session = self.connect()
        try:
            session.add(Mesure(methode=methode, anime_id=anime_id,
                               temps_ms=temps_ms, nb_resultats=nb_resultats))
            session.commit()
        finally:
            session.close()

    def findDernieres(self, limite=50):
        session = self.connect()
        try:
            return session.query(Mesure).order_by(Mesure.date_mesure.desc()).limit(limite).all()
        finally:
            session.close()

    def findTempsParMethode(self):
        """Toutes les paires (methode, temps_ms), pour calculer médiane et centiles."""
        session = self.connect()
        try:
            return session.query(Mesure.methode, Mesure.temps_ms).all()
        finally:
            session.close()

    def resume_par_methode(self):
        session = self.connect()
        try:
            return (
                session.query(
                    Mesure.methode,
                    func.count(Mesure.id),
                    func.min(Mesure.temps_ms),
                    func.max(Mesure.temps_ms),
                    func.avg(Mesure.temps_ms),
                )
                .group_by(Mesure.methode)
                .all()
            )
        finally:
            session.close()