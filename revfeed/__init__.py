from flask import Flask

from . import settings, views


def create_app():
    app = Flask(__name__)
    app.config.from_object(settings)
    app.register_blueprint(views.api)
    app.register_blueprint(views.pages)
    return app
