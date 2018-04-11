import os


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    DB_HOST = 'localhost'
    DB_USER = 'kojojo'
    DB_PASS = 'kojojo'
    DB_NAME = 'KOJOJO'
    UPLOAD_FILE = 'uploads'