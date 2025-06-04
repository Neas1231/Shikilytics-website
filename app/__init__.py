from flask import Flask
from flask_caching import Cache

app = Flask(__name__, template_folder='../templates',static_folder='../static')
cache = Cache(app, config={'CACHE_TYPE': 'simple'})

def create_app():
    from .main_routes import main
    from .funcs import funcs

    app.register_blueprint(main)
    app.register_blueprint(funcs)

    return app
