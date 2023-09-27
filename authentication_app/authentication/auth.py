# my_authentication_app/authentication/auth.py
from datetime import datetime, timedelta
import jwt
from jwt import ExpiredSignatureError, PyJWTError
from passlib.context import CryptContext
from fastapi import Request, HTTPException, Depends, Security, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pymongo.collection import Collection
from pymongo.database import Database
from pydantic import BaseModel

from .config import NoSQLUserDB, User, UserForm
from .postgresql_models import (SQLUserDB, 
                                update_pg_user_session, 
                                get_pg_user_session)
from .mongodb_models import (create_user,
                             find_user, 
                            update_mongo_user)

from .database import Database

# OAuth2PasswordBearer for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


# Password hashing
passlib_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Authentication class
class Auth:
    def __init__(self, db: Database):
        self.db = db

    def authenticate_user(self, form_data):
        user = None
        if self.db.config.use_database == "mongodb":
            user = find_user({"username": form_data.username})
            user_hash_password = user['hashed_password']
            session_id = user['session_id']

        elif self.db.config.use_database == "postgresql":
            user = get_pg_user_session(self.db, username=form_data.username)
            user_hash_password = str(user.hashed_password).strip()
            session_id = user.session_id

        # print(user)
        if not user:
            return False
        # print("user", user.username, "Length: ", len(user.hashed_password), "type", type(user))
        # print("Input hashed pass: ", len(self.get_password_hash(form_data.password)))

        if not self.verify_password(form_data.password, user_hash_password):
            return False

        return user
    
    # When a user signs in or accesses a protected endpoint
    def check_session_status(self, username):
        # Query the user's session status in the database
        if self.db.config.use_database == "postgresql":
            user_session = get_pg_user_session(self.db, username)
            if user_session and user_session.status == "active":
                return True
        elif self.db.config.use_database == "mongodb":
            collection = self.db.get_session().users
            user_session = collection.find_one({"username": username, "status": "active"})
            if user_session:
                return True



    def login(self, form_data):
        # Authenticate user
        user = self.authenticate_user(form_data)
        print("Auth user: ", user.username)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # prohibit multi user login on same 
        username = form_data.username
        if self.check_session_status(username):
            raise HTTPException(
                status_code=409, detail="User active in another session!")
        
        access_token_expires = timedelta(
            minutes=self.db.config.access_token_expire_minutes)

        if self.db.config.use_database == "postgresql":
            username = user.username
        elif self.db.config.use_database == "mongodb":
            username = user['username']
        print("username: ", username)
        access_token = self.create_access_token(
                            data={"sub": username}, 
                            expires_delta=access_token_expires,
                            status="active"
                        )
        return {"access_token": access_token, "token_type": "bearer"}


    def logout(self, user):
        if self.db.config.use_database == "postgresql":
            user = get_pg_user_session(self.db, user.username)
            update_pg_user_session(self.db, user.username, session=user.session_id, status="not active")
            user = get_pg_user_session(self.db, user.username)
        elif self.db.config.use_database == "mongodb":
            collection = self.db.get_session().users
            user = collection.update_one({"username": user.username}, {"$set": {"status": "not active"}})
        return {"user": user, "mssg": "sign out successfully"}

    # NoSql -> `NoSQLUserDB` format user
    # SQL -> `SQLUserDB`, MySQL, PostgreSQL, Sqlite
    def create_user(self, user: User):
        # print("Plain password: ", user.password, "type: ", type(user.password))
        hashed_password = self.get_password_hash(user.password)
        if self.db.config.use_database == "postgresql":
            # Create user in PostgreSQL
            db_user = SQLUserDB(username=user.username, 
                                hashed_password=hashed_password, 
                                is_superuser=user.is_superuser)
            db = self.db.get_session()
            db.add(db_user)
            db.commit()
            db.refresh(db_user)
            return db_user
        elif self.db.config.use_database == "mongodb":
            user_data = NoSQLUserDB(username=user.username, 
                                    hashed_password=hashed_password, 
                                    is_superuser=user.is_superuser)
            create_user(user_data)
            # user = self.db.get_session().users.insert_one(user_data.dict())
            return user_data
            
        else:
            raise ValueError("Invalid database type. Please choose 'postgresql' or 'mongodb'.")

    def create_access_token(self, data: dict, expires_delta: timedelta = None, status: str = "active"):
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.db.config.access_token_expire_minutes)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.db.config.secret_key, 
                                 algorithm=self.db.config.algorithm)

        if self.db.config.use_database == "mongodb":
            update_mongo_user({"username": data['sub']},  {
                        "$push": {"sessions": {encoded_jwt: {}}}, 
                        "$set": {"session_id": encoded_jwt, "status": status}})
        elif self.db.config.use_database == "postgresql":
            update_pg_user_session(self.db, username=data['sub'],
                                session=encoded_jwt, status=status)
         
        print(encoded_jwt)
        return encoded_jwt

    def verify_password(self, plain_password, hashed_password):
        return passlib_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password):
        return passlib_context.hash(password)

    def get_current_user(self, token: str = Depends(oauth2_scheme)):
        try:
            payload = jwt.decode(token, self.db.config.secret_key, 
                algorithms=[self.db.config.algorithm])
            username: str = payload.get("sub").strip()
            print("username", username, "username")
            if username is None:
                raise HTTPException(status_code=401, 
                                    detail="Could not validate credentials")
            if "exp" in payload:
                expiration_time = datetime.fromtimestamp(payload["exp"])
                current_time = datetime.utcnow()
                if current_time > expiration_time:
                    raise HTTPException(status_code=403, detail="Token expired!")
            
            if self.db.config.use_database == "postgresql":
                db_user = self.db.get_session().query(SQLUserDB)\
                            .filter(SQLUserDB.username == username)\
                            .first()
                if db_user is None:
                    raise HTTPException(status_code=401, detail="User not found")
                elif db_user.status != 'active':
                    raise HTTPException(
                        status_code=401, detail="You have logged out! Login again")
                return User(username=db_user.username, is_superuser=db_user.is_superuser)
            
            elif self.db.config.use_database == "mongodb":
                user_data = find_user({"username": username}) 
                if user_data is None:
                    raise HTTPException(
                        status_code=401, detail="User not found")
                elif user_data['status'] != 'active':
                    raise HTTPException(
                        status_code=401, detail="You have logged out! Login again")
                return User(username=user_data['username'], is_superuser=user_data['is_superuser'])
            else:
                raise ValueError("Invalid database type. Please choose 'postgresql' or 'mongodb'.")


        except ExpiredSignatureError:
            print(self.db.config.RAISE_EXPIRED_ERROR)
            if self.db.config.RAISE_EXPIRED_ERROR:
                raise HTTPException(status_code=403, detail="Token expired!")
            # return User(username=db_user.username)
            payload = jwt.decode(token, self.db.config.secret_key, 
                algorithms=[self.db.config.algorithm], options={"verify_signature": False})
            username: str = payload.get("sub").strip()
            # print("username", username, "username")
            self.db.config.RAISE_EXPIRED_ERROR = True
            return User(username=username, is_superuser=False)

        except PyJWTError as e:
            print(e)
            raise HTTPException(status_code=401, detail="Could not validate credentials")
   
    def find_me(self, username):       
        print(username, "username")
        if self.db.config.use_database == "postgresql":
            user = self.db.get_session().query(SQLUserDB).filter(SQLUserDB.username == username).first()
        elif self.db.config.use_database == "mongodb":
            collection = self.db.get_session().users
            user = collection.find_one({"username": username}, {"_id": False, "hashed_password": False})

        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user
 
def get_current_active_user(current_user: User = Security(Auth.get_current_user, scopes=["superuser"])):
    # Check user permissions
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    return current_user
