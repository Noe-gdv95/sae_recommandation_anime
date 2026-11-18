from sqlalchemy.orm import sessionmaker, selectinload
from app.models.base import get_engine
from app.models.anime import Anime
from app.models.association import anime_genre
from app.models.genre import Genre
from app.models.rating import Rating

class AnimeSqliteORM:
    def __init__(self, db_uri=None):
        self.engine = get_engine(db_uri)
        self.SessionFactory = sessionmaker(bind=self.engine, expire_on_commit=False)

    def connect(self):
        return self.SessionFactory()

    def _query_anime_full(self, session):
        return session.query(Anime).options(selectinload(Anime.genres))

    def findAll(self, recherche=None, genre_id=None, type_anime=None, limite=None):
        session = self.connect()
        try:
            query = self._query_anime_full(session)

            if recherche:
                query = query.filter(Anime.nom.ilike(f"%{recherche}%"))

            if genre_id :
                query = query.filter(Anime.genres.any(id=genre_id))

            if type_anime:
                query = query.filter(Anime.type == type_anime)

            query = query.order_by(Anime.nb_membres.desc())

            if limite:
                query = query.limit(limite)

            return query.all()

        finally:
            session.close()

    def findById(self, anime_id):
        session = self.connect()
        try:
            return self._query_anime_full(session).filter(Anime.id == anime_id).first()
        finally:
            session.close()

    def findByIds(self, ids):
        session = self.connect()
        try:
            animes = self._query_anime_full(session).filter(Anime.id.in_(ids)).all()
            return {anime.id: anime for anime in animes}
        finally:
            session.close()

    def findInfosAnimes(self):
        session = self.connect()
        try:
            return session.query(Anime.id, Anime.type, Anime.nb_membres).all()
        finally:
            session.close()

    def findLiensAnimeGenre(self):
        session = self.connect()
        try:
            return session.query(anime_genre.c.anime_id, anime_genre.c.genre_id).all()
        finally:
            session.close()

    def findAllGenres(self):
        session = self.connect()
        try:
            return session.query(Genre).order_by(Genre.nom).all()
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
        