import os

import pytest

from app import create_app, db
from app.models import BloodDonation, User, Donor, Inventory, Request


@pytest.fixture(scope='session')
def test_client():
    os.environ['CONFIG_TYPE'] = 'config.TestingConfig'
    flask_app = create_app()

    with flask_app.test_client() as testing_client:
        with flask_app.app_context():
            yield testing_client


@pytest.fixture(scope='session')
def init_database(test_client):
    db.create_all()

    yield db

    db.drop_all()
