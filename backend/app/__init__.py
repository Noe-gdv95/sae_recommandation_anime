from flask import Flask
from flask_cors import CORS
from app.blueprints import animes_bp, mesures_bp

def create_app():
    app = Flask(__name__)
    CORS(app)


    app.config['SECRET_KEY'] = 'cle-secrete-sae-anime'

    app.register_blueprint(animes_bp)
    app.register_blueprint(mesures_bp)

    @app.route('/')
    def home():
        return {"message" : "API de recommandation d'Animes en ligne"}
    
    return app
    