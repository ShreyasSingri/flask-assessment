from flask_restx import Resource, Namespace
from flask import request, jsonify

userNs = Namespace("user")

@userNs.route("/signup")
class Signup(Resource):
    def post(self):
        data = request.get_json()
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        return {'message': 'User registered successfully'}, 201