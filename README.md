
# FastAPI-Based Secure Authentication System

## Overview

Welcome to our FastAPI-based authentication system, designed to provide robust security and user management for your applications. Whether you're building a web application, API, or any other service, our authentication system is tailored to meet your needs.

## Key Features

- **Database Flexibility**: Our system seamlessly supports both SQL and NoSQL databases, making it compatible with popular database systems like PostgreSQL and MongoDB.

- **Custom User Creation**: You have the freedom to create new users with custom choices, ensuring that your user management aligns perfectly with your application's requirements.

- **Session Management**: We prioritize session security. Our system prohibits multiple user logins on the same account by default. However, you can choose to allow or disallow concurrent sessions based on your preferences.

- **Token Renewal**: Users can conveniently renew their authentication tokens, eliminating the need to log in repeatedly. It enhances user experience while maintaining security.

- **Enhanced Security**: If a user logs out or their access is revoked, they won't be able to access protected endpoints, even if their token is still valid. This robust security feature minimizes potential threats.

## How It Works

Here's how our approach works:

1. **Token Decoding**: When a request is made to a protected endpoint, we first decode the JSON Web Token (JWT) to extract the user's identity, typically their username.

2. **Database Query**: After decoding the token, we query the database based on the extracted username. This database query aims to fetch additional user information, specifically their session status.

3. **User Not Found Handling**: If the user is not found in the database, it means that the user is either not registered or their account has been deleted. In this case, we return a 401 Unauthorized response, ensuring that only authenticated users can access resources.

4. **Session Status Check**: Assuming the user is found in the database, we retrieve their session status. The session status indicates whether the user's session is active or not.

5. **Inactive Session Handling**: If the user's session status is "not active," it signifies that the user has either explicitly logged out or their access has been revoked. In this scenario, we also return a 401 Unauthorized response, reinforcing security measures.

This approach ensures that only authenticated and authorized users can access protected resources. It enhances security by managing user sessions and access privileges effectively. Even if an attacker gains access to a valid token, they cannot access protected endpoints if the user's session status is appropriately managed in the database.

Trust our FastAPI-based authentication system to fortify your application's security while delivering a seamless user experience.

## Get Started

Ready to boost your application's security and user management? Dive into our FastAPI-based authentication system now and experience the difference.

[Get Started](#) <!-- Add a link to your installation or setup guide here -->

## License

This project is licensed under the [MIT License](#). Feel free to use, modify, and distribute it according to your requirements.




## File Structure

```
authentication_app/
│
├── authentication_app/
│   ├── __init__.py
│   ├── authentication/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── auth.py
│   │   ├── db_models.py
│   │   ├── postgresql_models.py
│   │   ├── mongodb_models.py
│   │   └── database.py
│   └── ...
│
├── setup.py  # Package setup script
├── README.md
├── requirements.txt  # Dependencies
```

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
uvicorn authentication_app.main:app --reload
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

