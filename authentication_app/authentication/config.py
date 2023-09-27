# my_authentication_app/authentication/config.py
from pydantic_settings import BaseSettings
from pydantic.v1 import BaseModel, Field

class AuthConfig(BaseSettings):
    secret_key: str = "your-secret-key"  # Replace with a secure secret key
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 5
    use_database: str = "postgresql"  # Default to PostgreSQL

    # PostgreSQL configuration
    postgresql_uri: str = "postgresql+psycopg2://postgres:admin1234@localhost/auth"

    # MongoDB configuration
    mongodb_uri: str = "mongodb+srv://username:password@cluster.4m8b8.mongodb.net/"
    mongodb_db_name: str = "database"

    RAISE_EXPIRED_ERROR: bool =  True


class NoSQLUserDB(BaseModel):
    username: str
    hashed_password: str
    is_superuser: bool
    active_session: str = Field(default=None)
    role: str = Field(default='user')


class UserForm(BaseModel):
    username: str
    password: str
    is_superuser: bool = Field(default=False)
    role: str = Field(default='user')


class User(BaseModel):
    username: str
    is_superuser: bool


