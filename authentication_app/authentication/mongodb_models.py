# my_authentication_app/authentication/mongodb_models.py
from pydantic import BaseModel
from bson import ObjectId
from typing import Optional

class MongoDBUserDB(BaseModel):
    id: Optional[ObjectId]  # Optional for new user creation
    username: str
    hashed_password: str
    is_superuser: bool

class MongoDBTokenDB(BaseModel):
    id: ObjectId
    access_token: str
    token_type: str

class MongoDBUserCreate(BaseModel):
    username: str
    hashed_password: str
    is_superuser: bool
