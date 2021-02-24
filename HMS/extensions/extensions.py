from flask_jwt_extended import JWTManager
from flask_mongoengine import MongoEngine

db = MongoEngine()
jwt = JWTManager()
