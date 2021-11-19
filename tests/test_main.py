from fastapi.testclient import TestClient
from main import app, get_db
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from pytest import fixture

from database.database import Base


SQLITE_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLITE_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSession()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


@fixture()
def test_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def test_home(test_db):
    response = client.get('/')
    assert response.status_code != 400
    assert response.status_code == 200
    assert response.json() == {'status': 'ok', 'message': 'Hello users!'}


def test_create_user(test_db):
    response = client.post(
        '/create/',
        json={
            'email': 'test@mail.com',
            'password': 'secret_password',
            'name': 'John Doe'
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data['email'] == 'test@mail.com'


def test_create_user_fails_with_missing_attributes(test_db):
    response = client.post(
        '/create/',
        json={
            'email': 'test@mail.com'
        }
    )
    assert response.status_code == 422


def test_create_user_fails_to_create_the_same_user_multiple_times(test_db):
    client.post(
        '/create/',
        json={
            'email': 'test@mail.com',
            'password': 'secret_password',
            'name': 'John Doe'
        }
    )
    response = client.post(
        '/create/',
        json={
            'email': 'test@mail.com',
            'password': 'secret_password',
            'name': 'John Doe'
        }
    )
    assert response.status_code == 420
    data = response.json()
    assert data['message'] == 'error unexpected'


def test_users_list_returns_all_registered_emails(test_db):
    client.post(
        '/create/',
        json={
            'email': 'test@mail.com',
            'password': 'secret_password',
            'name': 'John Doe'
        }
    )
    client.post(
        '/create/',
        json={
            'email': 'test2@mail.com',
            'password': 'secret_password2',
            'name': 'John Doe 2'
        }
    )
    client.post(
        '/create/',
        json={
            'email': 'test3@mail.com',
            'password': 'secret_password3',
            'name': 'John Doe 3'
        }
    )

    response = client.get('/users_list')
    assert response.status_code == 200
    data = response.json()
    actual_users = set(data['users'])
    expected_users = set(['test@mail.com', 'test2@mail.com', 'test3@mail.com'])
    assert len(expected_users) == 3

    # Compare the content of 2 lists without caring for order:
    # setA ^ setB is the symmetric difference between sets
    # (no difference == lists have the same contents)
    assert not actual_users ^ expected_users


app.dependency_overrides = {}
