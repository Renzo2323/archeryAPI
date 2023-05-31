from flask import Flask
from .app import main

def createApp():
    app = Flask(__name__)

    app.register_blueprint(main)

    return app