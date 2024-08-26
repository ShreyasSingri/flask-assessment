## Flask assessment

# Blood Bank Management System

Blood bank management system is a flask-python project to handle backend services for all operations of backend. It is built using Flask, Flask-Restx, Flask-JWT-Extended and SQLAlchemy.

It has 5 different types of users namely User, DonorManager, InventoryManager, BankManager and Hospital having different permissions and ability to perform different operations.


## Requirements

- Python 3.8+
- SQLite (for local development)

## Installation

1. Clone the repository:

   git clone https://github.com/ShreyasSingri/flask-assessment
   cd flask-assessment


## Setup

Create a virtual environment and activate it:
```bash
python -m venv venv
./env/Scripts/Activate.bat       # On Mac:  source venv/bin/activate
```
Install the dependencies:
```bash
pip install -r requirements.txt
```
Create a .env file in the root directory and add the following environment variables:

env
```bash
FLASK_ENV=development
SECRET_KEY= your_secret_key
JWT_SECRET_KEY= your_jwt_secret
SQLALCHEMY_DATABASE_URI=sqlite:///blood_bank.db
```

Initialize the database:

```bash
flask db init
flask db migrate -m "Initial migration."
flask db upgrade
```
## Running the Application

Run the Flask application:

```bash
flask run
```
The API will be available at http://127.0.0.1:5000/


## Testing the application

Run test cases:

```bash
python -m pytest --cov=app
```