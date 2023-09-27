# my_authentication_app/authentication/mongodb_models.py
from pydantic.v1 import BaseModel, Field
from uuid import UUID, uuid4
from .database import db
from pymongo.errors import DuplicateKeyError
from fastapi import HTTPException
from datetime import datetime

# collection = db.get_session().users

# create indexes
# collection.create_index("username", unique=True)


class MongoDBUserDB(BaseModel):
    # Optional for new user creation
    id: UUID = Field(default_factory=uuid4, alias='_id')
    username: str = Field()
    hashed_password: str = Field()
    is_superuser: bool
    sessions: list = Field(default=[])
    session_id: str = Field(default='')
    status: str = Field(default='Not activte')
    created_at = Field(default=datetime.utcnow())
    role: str = Field(default='user')

    class Config:
        allow_population_by_field_name = True

        schema_extra = {
                "example": {
                    "id": "066de609-b04a-4b30-b46c-32537c7f1f6e",
                    "username": "Don Quixote",
                    "hashed_password": "1231edsadcae2",
                    "is_superuser": "false",
                    "role": 'user',
                }
        }


def create_user(user_data):
    try:
        collection = db.get_session().users
        res = collection.insert_one(
            user_data.dict())
        return res

    except DuplicateKeyError:
        raise HTTPException(status_code=409, detail="User already exists!")

    except Exception:
        raise HTTPException(status_code=500, detail="Something went wrong!")


def find_user(query):
    try:
        collection = db.get_session().users
        res = collection.find_one(query)
        return res
    except Exception:
        raise HTTPException(status_code=500, detail="Something went wrong!")


def update_mongo_user(query, data):
    try:
        collection = db.get_session().users
        collection.update_one(query, data)
    except Exception:
        raise HTTPException(status_code=500, detail="Something went wrong!")
