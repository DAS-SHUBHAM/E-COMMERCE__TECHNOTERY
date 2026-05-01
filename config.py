import os
from dotenv import load_dotenv
from datetime import timedelta
# Load the variables from the .env file into the system
load_dotenv()

class Config:
    # Flask Core
    SECRET_KEY = os.getenv('SECRET_KEY', 'fallback_secret_key')
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # JWT
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'fallback_jwt_key')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=7)
    
    # Mail Server Setup
    # Mail Server Setup
    MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.getenv('MAIL_PORT', 587))
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', 'True') == 'True'
    
    # FIX: Look for the variable names from the .env file!
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = ("MithilaRoots",os.getenv('MAIL_USERNAME'))