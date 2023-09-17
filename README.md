# Authentication App

This is a flexible authentication app that allows you to choose between MongoDB and PostgreSQL as the backend database.

## Installation

1. Clone this repository:
```
git clone https://github.com/yourusername/my_authentication_app.git

cd authentication_app

```


2. Create a virtual environment (optional but recommended:
```python
python -m venv venv
source venv/bin/activate
```


3. Install the required dependencies:

```python
pip install -r requirements.txt
```


## Configuration

You can configure the choice of backend database in the `authentication/config.py` file by setting the `use_database` parameter to either "postgresql" or "mongodb."

## Usage

1. Run the application:

```
uvicorn my_authentication_app.main:app --reload
```

2. Access the Swagger documentation at http://localhost:8000/docs to interact with the API endpoints.



## Integrate with any applications

```python
from authentication_app.authentication.auth import Auth

from fastapi import Depends, FastAPI

app = FastAPI()
auth = Auth()  # Create an instance of the Auth class

@app.get("/protected", response_model=str)
def protected_endpoint(current_user: str = Depends(auth.get_current_user)):
    # Your protected endpoint logic here
    return "This is a protected endpoint."
```


## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

