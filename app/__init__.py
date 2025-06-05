from flask import Flask

app = Flask(__name__, template_folder='../templates',static_folder='../static')

def create_app():
    from .main_routes import main
    from .funcs import funcs

    app.register_blueprint(main)
    app.register_blueprint(funcs)

    return app
