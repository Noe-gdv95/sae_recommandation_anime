from flask import Blueprint, jsonify
from app.services.MesureService import MesureService

mesures_bp = Blueprint('mesures', __name__)
mesure_service = MesureService()

@mesures_bp.route('/api/mesures', methods=['GET'])
def get_mesures():
    return jsonify(mesure_service.get_dernieres_mesures())

@mesures_bp.route('/api/mesures/resume', methods=['GET'])
def get_resume():
    return jsonify(mesure_service.get_resume())