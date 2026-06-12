import pytest

from app import create_app
from database import db
from models import Usuario


@pytest.fixture()
def flask_app():
    app = create_app(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        }
    )

    with app.app_context():
        db.create_all()

    return app


@pytest.fixture
def client(flask_app):
    with flask_app.test_client() as client:
        yield client


def test_home(client):
    response = client.get("/")
    assert response.status_code == 200


def test_about(client):
    response = client.get("/about")
    assert response.status_code == 200


def test_register_and_login(client):
    register_response = client.post(
        "/api/auth/register",
        json={
            "usuario": "tester",
            "contrasena": "secreto123",
            "nombres": "Usuario",
            "apellidos": "Prueba",
        },
    )
    assert register_response.status_code == 201
    assert register_response.get_json()["usuario"]["usuario"] == "tester"

    login_response = client.post(
        "/api/auth/login",
        json={
            "usuario": "tester",
            "contrasena": "secreto123",
        },
    )
    assert login_response.status_code == 200
    assert login_response.get_json()["usuario"]["nombres"] == "Usuario"


def test_login_rejects_wrong_password(client):
    client.post(
        "/api/auth/register",
        json={
            "usuario": "tester",
            "contrasena": "secreto123",
            "nombres": "Usuario",
        },
    )

    response = client.post(
        "/api/auth/login",
        json={
            "usuario": "tester",
            "contrasena": "incorrecta",
        },
    )
    assert response.status_code == 401


def test_login_migrates_legacy_plain_password(client, flask_app):
    with flask_app.app_context():
        db.session.add(
            Usuario(
                usuario="legacy",
                contrasena_hash="temporal123",
                nombres="Usuario",
            )
        )
        db.session.commit()

    response = client.post(
        "/api/auth/login",
        json={
            "usuario": "legacy",
            "contrasena": "temporal123",
        },
    )
    assert response.status_code == 200

    with flask_app.app_context():
        usuario = Usuario.query.filter_by(usuario="legacy").first()
        assert usuario.contrasena_hash != "temporal123"
