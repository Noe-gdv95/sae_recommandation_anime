from sqlalchemy import func
from sqlalchemy.orm import sessionmaker
from app.models.base import get_engine
from app.models.mesure import Mesure

class MesureSqliteORM:
    def init(self, db_uri=None):
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

