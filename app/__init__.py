from .instances import db, migrate, login_manager
from .Routes.main import main_bp
from .Routes.auth import auth_bp
from .Routes.game import game_bp
from .Routes.vote import vote_bp
from .Routes.comment import comment_bp
from .Routes.search_filter import search_bp
from dotenv import load_dotenv
from flask_dance.contrib.google import google
from flask_cors import CORS
from flask import Flask
import os

load_dotenv()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['CORS_HEADERS'] = 'Content-Type'
    app.config['CORS_SUPPORTS_CREDENTIALS'] = True
    app.config['CORS_EXPOSE_HEADERS'] = ['Content-Type', 'Authorization']
    app.config['CORS_ALLOW_HEADERS'] = ['Content-Type', 'Authorization']
    app.config['CORS_ALLOW_METHODS'] = ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS']
    app.config['CORS_ALLOW_ORIGINS'] = ['*']
    app.config['CORS_MAX_AGE'] = 3600
    app.config['GOOGLE_CLIENT_ID'] = os.getenv('GOOGLE_CLIENT_ID')
    app.config['GOOGLE_CLIENT_SECRET'] = os.getenv('GOOGLE_CLIENT_SECRET')

    def init_oauth(app):
    google_bp = make_google_blueprint(
        client_id=app.config['GOOGLE_CLIENT_ID'],
        client_secret=app.config['GOOGLE_CLIENT_SECRET'],
        scope=['profile', 'email'],
        redirect_url="/auth/google/callback"
    )

    app.register_blueprint(google_bp, url_prefix="/auth/google")

    login_manager.init_app(app)
    migrate.init_app(app, db)
    db.init_app(app)

    init_oauth(app)

    CORS(app)

    app.register_blueprint(main_bp, url_prefix='/')
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(game_bp, url_prefix='/game')
    app.register_blueprint(vote_bp, url_prefix='/vote')
    app.register_blueprint(comment_bp, url_prefix='/comment')
    app.register_blueprint(search_bp, url_prefix='/search')

    with app.app_context():
        db.create_all()
        db.session.commit()
    return app