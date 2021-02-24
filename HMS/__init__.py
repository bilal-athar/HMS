from flask import Flask
from HMS import config
from flask_cors import CORS


def create_app(config_file='config.py'):
    app = Flask(__name__)
    CORS(app)
    app.config.from_pyfile(config_file)

    from .extensions.extensions import db
    db.init_app(app)

    from .extensions.extensions import jwt
    jwt.init_app(app)

    from .views.doctors import db_users
    app.register_blueprint(db_users)

    from .views.patient import patient
    app.register_blueprint(patient)

    return app
