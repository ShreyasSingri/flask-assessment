from flask_sqlalchemy import SQLAlchemy
from flask_restx import Api
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
authorizations = {
    'Bearer': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'Authorization'
    }
}
api = Api(authorizations=authorizations, security='Bearer')
db = SQLAlchemy()
migrate = Migrate()
bcrypt = Bcrypt()