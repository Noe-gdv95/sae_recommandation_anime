from sqlalchemy.orm import sessionmaker, selectinload
from app.models.base import get_engine
from app.models.anime import Anime
from app.models.genre import Genre

class AnimeSqliteORM:
    def __init__(self, db_uri=None):
        self.engine = get_engine(db_uri)
        self.SessionFactory = sessionmaker(bind=self.engine, expire_on_commit=False)

    def connect(self):
        return self.SessionFactory()

    def _query_anime_full(self, session):
        return session.query(Anime).options(selectinload(Anime.genres))

    def findAll(self, genre_id = None, type_anime = None):
        session = self.connect()
        try:
            query = self._query_anime_full(session)

            if genre_id :
                query = query.filter(Anime.genres.any(id=genre_id))
            
            if type_anime:
                query = query.filter(Anime.type == type_anime)
            
            return query.order_by(Anime.nom).all()
        
        finally:
            session.close()

    def get_home_stats(self):
        session = self.connect()
        try:
            return{
                "animes_count" : session.query(Anime).count(),
                "genres_count" : session.query(Genre).count()
            }
        finally:
            session.close()
        