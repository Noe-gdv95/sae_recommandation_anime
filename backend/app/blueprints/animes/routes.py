from flask import Blueprint, jsonify, request
from app.services.AnimeService import AnimeService

animes_bp = Blueprint('animes', __name__)
anime_service = AnimeService()


def anime_vers_dict(anime):
    return {
        "id": anime.id,
        "nom": anime.nom,
        "type": anime.type,
        "nb_episodes": anime.nb_episodes,
        "note_moyenne": anime.note_moyenne,
        "nb_membres": anime.nb_membres,
        "genres": [genre.nom for genre in anime.genres],
    }


@animes_bp.route('/api/stats', methods=['GET'])
def get_stats():
    stats = anime_service.get_home_stats()
    return jsonify(stats)

@animes_bp.route('/api/animes', methods=['GET'])
def get_animes():
    recherche = request.args.get('q', type=str)
    genre_id = request.args.get('genre_id', type=int)
    type_anime = request.args.get('type_anime', type=str)
    limite = request.args.get('limit', default=20, type=int)
    limite = max(1, min(limite, 100))

    animes = anime_service.get_all_animes(recherche=recherche, genre_id=genre_id, type_anime=type_anime, limite=limite)

    result = []
    for anime in animes:
        result.append(anime_vers_dict(anime))

    return jsonify(result)

@animes_bp.route('/api/animes/<int:anime_id>', methods=['GET'])
def get_anime(anime_id):
    anime = anime_service.get_anime_by_id(anime_id)
    if anime is None:
        return jsonify({"erreur": "Anime introuvable"}), 404
    return jsonify(anime_vers_dict(anime))
