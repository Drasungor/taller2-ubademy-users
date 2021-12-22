from fastapi.testclient import TestClient
from main import app, get_db
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from pytest import fixture
from unittest.mock import patch, MagicMock

from database.database import Base
from configuration.status_messages import public_status_messages


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

# TODO: tengo que agregar el header de api key a los tests porque
#   la verificacion se hace en un middleware.
#   Lo ideal es cambiarlo a una dependencia que se pueda overridear
HEADER = {'Authorization': 'db927b6105712695971a38fa593db084d95f86f68a1f85030ff5326d7a30c673'}


@fixture()
def test_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def test_home(test_db):
    response = client.get('/', headers=HEADER)
    assert response.status_code != 400
    assert response.status_code == 200
    assert response.json() == public_status_messages.get_message('hello_users')


def test_create_user(test_db):
    response = client.post(
        '/create/',
        json={
            'email': 'test@mail.com',
            'password': 'secret_password',
            'expo_token': 'expo12345token'
        },
        headers=HEADER
    )
    assert response.status_code == 200
    data = response.json()
    assert data['email'] == 'test@mail.com'


def test_create_user_fails_with_missing_attributes(test_db):
    response = client.post(
        '/create/',
        json={
            'email': 'test@mail.com'
        },
        headers=HEADER
    )
    assert response.status_code == 422


def test_create_user_fails_to_create_the_same_user_multiple_times(test_db):
    client.post(
        '/create/',
        json={
            'email': 'test@mail.com',
            'password': 'secret_password',
            'expo_token': 'expo12345token'
        },
        headers=HEADER
    )
    response = client.post(
        '/create/',
        json={
            'email': 'test@mail.com',
            'password': 'secret_password',
            'expo_token': 'expo12345token'
        },
        headers=HEADER
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
            'expo_token': 'expo12345token'
        },
        headers=HEADER
    )
    client.post(
        '/create/',
        json={
            'email': 'test2@mail.com',
            'password': 'secret_password2',
            'expo_token': 'expo12345token'
        },
        headers=HEADER
    )
    client.post(
        '/create/',
        json={
            'email': 'test3@mail.com',
            'password': 'secret_password3',
            'expo_token': 'expo12345token'
        },
        headers=HEADER
    )

    response = client.get('/users_list/true', headers=HEADER)
    assert response.status_code == 200
    data = response.json()
    actual_users = set(map(lambda x: x['email'], data['users']))
    expected_users = set(['test@mail.com', 'test2@mail.com', 'test3@mail.com'])
    assert len(expected_users) == 3

    # Compare the content of 2 lists without caring for order:
    # setA ^ setB is the symmetric difference between sets
    # (no difference == lists have the same contents)
    assert not actual_users ^ expected_users


def test_oauth_login_registers_new_user(test_db):
    response = client.post(
        '/oauth_login',
        json={
            'email': 'test_mail@gmail.com',
            'expo_token': 'expo12345token'
        },
        headers=HEADER
    )
    response_data = response.json()

    assert response.status_code != 400
    assert response.status_code == 200
    assert response_data['status'] == 'ok'
    assert 'firebase_password' in response_data
    assert response_data['created']
    assert response_data['message'] == 'user successfully registered'


def test_oauth_login_does_not_register_existing_user_again(test_db):
    client.post(
        '/oauth_login',
        json={
            'email': 'test_mail@gmail.com',
            'expo_token': 'expo12345token'
        },
        headers=HEADER
    )

    response = client.post(
        '/oauth_login',
        json={
            'email': 'test_mail@gmail.com',
            'expo_token': 'expo12345token'
        },
        headers=HEADER
    )
    response_data = response.json()

    assert response.status_code != 400
    assert response.status_code == 200
    assert response_data['status'] == 'ok'
    assert 'firebase_password' in response_data
    assert not response_data['created']
    assert response_data['message'] == 'google account exists'


def test_change_block_status_can_block_user(test_db):
    client.post(
        '/create/',
        json={
            'email': 'test@mail.com',
            'password': 'secret_password',
            'expo_token': 'expo12345token'
        },
        headers=HEADER
    )

    response = client.post(
        '/change_blocked_status',
        json={
            'modified_user': 'test@mail.com',
            'is_blocked': True
        },
        headers=HEADER
    )

    response_data = response.json()

    assert response.status_code != 400
    assert response.status_code == 200
    assert response_data['status'] == 'ok'
    assert response_data['message'] == 'user updated'


def test_change_block_status_can_unblock_user(test_db):
    client.post(
        '/create/',
        json={
            'email': 'test@mail.com',
            'password': 'secret_password',
            'expo_token': 'expo12345token'
        },
        headers=HEADER
    )

    response = client.post(
        '/change_blocked_status',
        json={
            'modified_user': 'test@mail.com',
            'is_blocked': False
        },
        headers=HEADER
    )

    response_data = response.json()

    assert response.status_code != 400
    assert response.status_code == 200
    assert response_data['status'] == 'ok'
    assert response_data['message'] == 'user updated'


@patch('main.requests.post')
def test_send_message(mock_expo_api, test_db):
    mock_expo_api.return_value = MagicMock(status_code=200)

    res = client.post(
        '/create/',
        json={
            'email': 'receiver@mail.com',
            'password': 'secret_password',
            'expo_token': 'expo12345token'
        },
        headers=HEADER
    )

    assert res.status_code == 200

    response = client.post(
        '/send_message',
        json={
            'email': 'sender@mail.com',
            'user_receiver_email': 'receiver@mail.com',
            'message_body': 'this is my first message, how are you?'
        },
        headers=HEADER
    )

    response_data = response.json()

    assert response.status_code != 400
    assert response.status_code == 200
    assert response_data['status'] == 'ok'
    assert 'message' in response_data


app.dependency_overrides = {}
