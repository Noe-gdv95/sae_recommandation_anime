from flask import Blueprint, jsonify, request
from app.services.AnimeService import AnimeService
from app.services.ContenuService import ContenuService
from app.services.MesureService import MesureService

animes_bp = Blueprint('animes', __name__)
anime_service = AnimeService()
mesure_service = MesureService()

services_recommandation = {
    ContenuService.METHODE: ContenuService(),
}


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


@animes_bp.route('/api/animes/<int:anime_id>/recommandations', methods=['GET'])
def get_recommandations(anime_id):
    methode = request.args.get('methode', default='contenu', type=str)
    limite = request.args.get('limit', default=10, type=int)
    limite = max(1, min(limite, 50))

    service = services_recommandation.get(methode)
    if service is None:
        return jsonify({"erreur": f"Méthode '{methode}' indisponible"}), 404

    if anime_service.get_anime_by_id(anime_id) is None:
        return jsonify({"erreur": "Anime introuvable"}), 404

    recos, temps_ms = mesure_service.chronometrer(methode, anime_id, service.recommander, anime_id, limite)

    return jsonify({
        "methode": methode,
        "anime_id": anime_id,
        "temps_ms": round(temps_ms, 2),
        "recommandations": [
            {
                "anime": anime_vers_dict(reco["anime"]),
                "score": reco["score"],
                "genres_communs": reco["genres_communs"],
            }
            for reco in recos
        ],
    })
