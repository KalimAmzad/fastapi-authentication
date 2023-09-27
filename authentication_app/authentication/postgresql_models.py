# my_authentication_app/authentication/postgresql_models.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from datetime import datetime
from sqlalchemy.ext.declarative import declarative_base
from pydantic.v1 import BaseModel, Field

Base = declarative_base()

class SQLUserDB(Base):
    __tablename__ = "users"
    # __table_args__ = {'schema': 'pubic'}

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, index=True)
    hashed_password = Column(String)
    # active_session = Column(String)
    session_id = Column(String, unique=True)
    status = Column(String, default='not active')
    created_at = Column(DateTime, default=datetime.utcnow)
    is_superuser = Column(Boolean, default=False)


class ActiveSession(Base):
    __tablename__ = "active_sessions"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    token = Column(String, unique=True, index=True)
    username = Column(String, index=True)
    expiration_time = Column(DateTime)


def invalidate_previous_session(db, username):
    # Find and delete the previous session
    db_session = db.get_session()
    previous_session = db_session.query(SQLUserDB).filter(SQLUserDB.username == username).order_by(SQLUserDB.created_at.desc()).first()

    if previous_session:
        db_session.delete(previous_session)
        db_session.commit()

def update_pg_user_session(db, username, session, status):
    db = db.get_session()
    print(username)
    user_to_update = db.query(SQLUserDB).filter_by(username=username.strip()).first()
    if user_to_update:
        # Update the "active_session" attribute
        user_to_update.session_id = session
        user_to_update.status = status
        db.commit()
        print(f"Updated active session for user : {username}")
    else:
        print(f"User not found: {username}")

    # Close the session
    db.close()

def get_pg_user_session(db, username):
    db = db.get_session()
    user = db.query(SQLUserDB).filter_by(username=username).first()
    db.close()
    return user
