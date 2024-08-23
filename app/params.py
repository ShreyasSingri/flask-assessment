from flask_restx import fields
from .extentions import api

a = {
    "name":fields.String(required=True, description='The email')
}