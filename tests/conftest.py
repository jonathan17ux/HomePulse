import pytest

from src.app import create_app
from src.extensions import db


@pytest.fixture
def app(tmp_path):

    database_path = tmp_path / "homepulse_test.db"

    app = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI":
            f"sqlite:///{database_path}",
    })

    with app.app_context():
        db.create_all()

    yield app

    with app.app_context():
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()
