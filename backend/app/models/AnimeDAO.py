from sqlalchemy.orm import sessionmaker
from app.models.base import get_engine
from app.models.anime import Anime
from app.models.genre import Genre

class AnimeSqliteORM:
    def __init__(self, db_uri=None):
        self.engine = get_engine(db_uri)
        self.SessionFactory = sessionmaker(bind=self.engine, expire_on_commit=False)

    def connect(self):
        return self.SessionFactory()

    def get_home_stats(self):
        session = self.connect()
        try:
            return{
                "animes_count" : session.query(Anime).count(),
                "genres_count" : session.query(Genre).count()
            }
        finally:
            session.close()
        