import os
import redis  # Imported for In-Memory caching (OTP and session tokens)
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
from flask_mail import Mail
from flask_socketio import SocketIO

# Initialize Core Flask Extensions
db = SQLAlchemy()
jwt = JWTManager()
bcrypt = Bcrypt()
migrate = Migrate()
mail = Mail()

# Initialize SocketIO for real-time bidirectional communication
socketio = SocketIO(cors_allowed_origins="*")

# Initialize Redis Client Instance
# Configured via environment variables with fallback settings for local development
redis_client = redis.Redis(
    host=os.getenv('REDIS_HOST', 'localhost'),
    port=int(os.getenv('REDIS_PORT', 6379)),
    db=int(os.getenv('REDIS_DB', 0)),
    password=os.getenv('REDIS_PASSWORD', None),
    decode_responses=True  # Automatically decodes responses from bytes to strings
)