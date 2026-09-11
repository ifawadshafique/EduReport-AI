import os


class Config:
    SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "fallback-secret-key")
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "fallback-secret-key")
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class DevelopmentConfig(Config):
    DEBUG = True
    _db = os.environ.get("DATABASE_URL", "sqlite:///edureport.db")
    if _db.startswith("sqlite") and "check_same_thread" not in _db:
        if "?" in _db:
            _db += "&check_same_thread=False"
        else:
            _db += "?check_same_thread=False"
    SQLALCHEMY_DATABASE_URI = _db


class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")
