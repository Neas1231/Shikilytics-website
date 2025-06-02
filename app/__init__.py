from flask import Flask

def create_app():
    app = Flask(__name__, template_folder='../templates',static_folder='../static')

    from .main_routes import main
    from .funcs import funcs

    app.register_blueprint(main)
    app.register_blueprint(funcs)

    return app
