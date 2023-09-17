# my_authentication_app/authentication/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database
from pydantic import BaseSettings
import config
class Database:
    def __init__(self, config: AuthConfig):
        self.config = config

    def get_session(self):
        if self.config.use_database == "postgresql":
            engine = create_engine(self.config.postgresql_uri)
            SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
            return SessionLocal()
        elif self.config.use_database == "mongodb":
            client = MongoClient(self.config.mongodb_uri)
            db = client[self.config.mongodb_db_name]
            return db
        else:
            raise ValueError("Invalid database type. Please choose 'postgresql' or 'mongodb'.")

# config = AuthConfig()
db = Database(config)
