import os
from flask import Flask
from flask_cors import CORS
from flask_session import Session
from flask_socketio import SocketIO
from dotenv import load_dotenv

load_dotenv()

socketio = SocketIO(cors_allowed_origins="*")

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-key-12345')

    # Session configuration
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['SESSION_PERMANENT'] = False
    app.config['SESSION_USE_SIGNER'] = True

    Session(app)
    CORS(app, supports_credentials=True)
    socketio.init_app(app)

    from .routes import auth, emails
    app.register_blueprint(auth.bp)
    app.register_blueprint(emails.bp)

    return app
