from flask import Flask
import logging
from config import Config
from .extentions import api, db, bcrypt, migrate, jwt
from .routes import register_routes

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    api.init_app(app)
    migrate.init_app(app,db)
    db.init_app(app)
    jwt.init_app(app)
    bcrypt.init_app(app)
    register_routes(api)
    logging.basicConfig(filename='app.log', level=logging.ERROR, format='%(asctime)s:%(levelname)s:%(message)s')

    return app
