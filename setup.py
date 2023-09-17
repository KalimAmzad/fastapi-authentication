from setuptools import setup, find_packages

setup(
    name="authentication_app",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "fastapi==0.68.1",
        "uvicorn==0.15.0",
        "passlib[bcrypt]==1.7.4",
        "pydantic==1.8.3",
        "jose[cryptography]==1.3.2",
        "asyncpg==0.24.0",  # PostgreSQL driver (optional)
        "pymongo==3.12.1",  # MongoDB driver (optional)
        "python-multipart==0.0.5",
    ],
)
