import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'safira-music-cloud-secret'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///safira.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
