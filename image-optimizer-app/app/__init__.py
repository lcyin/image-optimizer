from flask import Flask

def configure_app(app):
    app.config.from_mapping(
        SECRET_KEY='dev',
    )

def create_app():
    app = Flask(__name__, instance_relative_config=True)
    configure_app(app)

    try:
        app.config.from_pyfile('config.py', silent=True)
    except FileNotFoundError:
        pass
    
    with app.app_context():
        from . import routes

    return app