# my_authentication_app/authentication/auth.py
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, Depends, Security
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pymongo.collection import Collection
from pymongo.database import Database
from pydantic import BaseModel

from .config import config
from .db_models import UserDB as PostgresUserDB
from .mongodb_models import UserDB as MongoDBUserDB
from .database import Database

# OAuth2PasswordBearer for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Pydantic models
class UserCreate(BaseModel):
    username: str
    password: str

class User(BaseModel):
    username: str
    is_superuser: bool

class Token(BaseModel):
    access_token: str
    token_type: str

# Password hashing
passlib_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Authentication class
class Auth:
    def __init__(self, db: Database):
        self.db = db

    def create_user(self, user: UserCreate, is_superuser: bool = False):
        if self.db.config.use_database == "postgresql":
            # Create user in PostgreSQL
            hashed_password = self.get_password_hash(user.password)
            db_user = PostgresUserDB(username=user.username, hashed_password=hashed_password, is_superuser=is_superuser)
            db = self.db.get_session()
            db.add(db_user)
            db.commit()
            db.refresh(db_user)
            return db_user
        elif self.db.config.use_database == "mongodb":
            user_data = MongoDBUserCreate(username=user.username, hashed_password=user.password, is_superuser=is_superuser)
            user_id = self.db.user_collection.insert_one(user_data.dict()).inserted_id
            return user_id
        else:
            raise ValueError("Invalid database type. Please choose 'postgresql' or 'mongodb'.")

    def create_access_token(self, data: dict, expires_delta: timedelta = None):
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=config.access_token_expire_minutes)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, config.secret_key, algorithm=config.algorithm)
        return encoded_jwt

    def verify_password(self, plain_password, hashed_password):
        return passlib_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password):
        return passlib_context.hash(password)

    def get_current_user(self, token: str = Depends(oauth2_scheme)):
        try:
            payload = jwt.decode(token, config.secret_key, algorithms=[config.algorithm])
            username: str = payload.get("sub")
            if username is None:
                raise HTTPException(status_code=401, detail="Could not validate credentials")
            token_data = TokenData(username=username)
        except JWTError:
            raise HTTPException(status_code=401, detail="Could not validate credentials")
        
        if self.db.config.use_database == "postgresql":
            db_user = self.db.get_session().query(PostgresUserDB).filter(PostgresUserDB.username == token_data.username).first()
            if db_user is None:
                raise HTTPException(status_code=401, detail="User not found")
            return User(username=db_user.username, is_superuser=db_user.is_superuser)
        elif self.db.config.use_database == "mongodb":
            user_data = self.db.user_collection.find_one({"username": token_data.username})
            if user_data is None:
                raise HTTPException(status_code=401, detail="User not found")
            user_db = MongoDBUserDB(**user_data)
            return User(username=user_db.username, is_superuser=user_db.is_superuser)
        else:
            raise ValueError("Invalid database type. Please choose 'postgresql' or 'mongodb'.")

def get_current_active_user(current_user: User = Security(Auth.get_current_user, scopes=["superuser"])):
    # Check user permissions
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    return current_user
