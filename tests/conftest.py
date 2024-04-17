import pytest
from src import app, db

@pytest.fixture()
def test_app():
    
    app.config.update({
        "TESTING": True 
    })
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.db"
    
    with app.app_context():
        db.create_all()
    
    yield app

@pytest.fixture()
def client(test_app):
    return test_app.test_client()