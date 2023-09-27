from fastapi import FastAPI, Header, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from typing import Annotated
import jwt
from jwt  import ExpiredSignatureError
from authentication.auth import Auth, User, UserForm
from authentication.database import db
from authentication.postgresql_models import SQLUserDB, invalidate_previous_session

app = FastAPI()
auth = Auth(db)
AUTH_ACCESS_TOKEN_EXPIRE_MINUTES = 5


@app.post("/login")
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    return auth.login(form_data)

@app.post("/signup")
async def signup(form_data: Annotated[UserForm, Depends()]):
    print(form_data)
    return auth.create_user(form_data)

@app.post("/logout/{username}")
async def logout(current_user: User = Depends(auth.get_current_user)):
    username = current_user.username
    print(current_user)
    if not username:
        raise HTTPException(status_code=404, detail="User not found")
    return auth.logout(current_user)

db.config.RAISE_EXPIRED_ERROR = False
# Function to handle token renewal
@app.post("/renew-token")
async def renew_token(temp: bool =  db.config.RAISE_EXPIRED_ERROR, current_user: User = Depends(auth.get_current_user)):
    # If Allow Multiple Concurrent Logins
    # Don't invalidate the previous session
    # If Single Active Session per User
    # Invalidate the previous session (if any)
    # invalidate_previous_session(db, current_user.username)
    # Generate a new access token
    # db.config.RAISE_EXPIRED_ERROR = False
    new_token = auth.create_access_token( data={"sub": current_user.username})
    print(new_token)
    return {"access_token": new_token, "token_type": "bearer", "message": "Token renewed"}


@app.get("/me")
async def get_user_by_name(current_user: User = Depends(auth.get_current_user)):
    # print(current_user)
    username = current_user.username.strip()
    return auth.find_me(username)


@app.get("/all")
async def get_all_users():
    if db.config.use_database == "postgresql":
        all_users = db.get_session().query(SQLUserDB).all()
    elif db.config.use_database == "mongodb":
        collection = db.get_session().users
        all_users = list(collection.find({}, {"_id": False, "hashed_password": False}))
    return all_users

@app.get("/", response_model=str)
async def index():
    return "This is an open endpoint."

@app.get("/protected", response_model=str)
async def protected_endpoint(current_user: User = Depends(auth.get_current_user)):
    return "This is a protected endpoint."

@app.get("/super_protected", response_model=str)
async def super_protected_endpoint(current_user: User = Depends(auth.get_current_user)):
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Access denied")
    return "This is a super-protected endpoint."
