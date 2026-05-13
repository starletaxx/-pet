import os

class Config:
    # SQLALCHEMY_DATABASE_URI = 'sqlite:///heartbeat.db'
    # Format: mysql+pymysql://username:password@host:port/databasename
    # Please update the username and password accordingly. 
    # Defaulting to root:root for local dev.
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:123456@localhost/hailToSun'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'dev-secret-key'
