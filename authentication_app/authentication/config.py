# my_authentication_app/authentication/config.py
from pydantic import BaseSettings

class AuthConfig(BaseSettings):
    secret_key: str = "your-secret-key"  # Replace with a secure secret key
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    use_database: str = "postgresql"  # Default to PostgreSQL

    # PostgreSQL configuration
    postgresql_uri: str = "postgresql://username:password@localhost/database_name"

    # MongoDB configuration
    mongodb_uri: str = "mongodb://localhost:27017/"
    mongodb_db_name: str = "my_auth_db"

config = AuthConfig()
