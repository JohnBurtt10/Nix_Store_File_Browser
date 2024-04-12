from flask import Flask
from flask_socketio import SocketIO

# Create the Flask application instance
app = Flask(__name__)

# Initialize SocketIO
socketio = SocketIO(app)

# Import routes (this should be done after creating the app instance)
from app import routes
from app import socketio_handlers