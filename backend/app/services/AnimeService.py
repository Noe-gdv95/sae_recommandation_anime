from app.models.AnimeDAO import AnimeSqliteORM

class AnimeService:
    def __init__(self):
        self.dao = AnimeSqliteORM()

    def get_all_animes(self, recherche=None, genre_id=None, type_anime=None, limite=None):
        return self.dao.findAll(recherche=recherche, genre_id=genre_id, type_anime=type_anime, limite=limite)

    def get_anime_by_id(self, anime_id):
        return self.dao.findById(anime_id)

    def get_all_genres(self):
        return self.dao.findAllGenres()

    def get_home_stats(self):
        return  self.dao.get_home_stats()

