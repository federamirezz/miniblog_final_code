import os

class Config:
    SECRET_KEY = '9b8a0f0c7e9f4a5b1d2c3e4f5a6b7c89d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5'
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root@localhost/miniblog'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
