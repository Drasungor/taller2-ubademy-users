import uvicorn

from fastapi import FastAPI, HTTPException

from models.user import User, fake_users_db
from models.login_data import Login
from models.registration_data import RegistrationData
from models.admin_registration_data import AdminRegistrationData
from models.admin_login_data import AdminLogin
from sqlalchemy import create_engine, exc
from sqlalchemy.orm import sessionmaker
import database_models.user as db_user
import database_models.admin as db_admin
from passlib.hash import pbkdf2_sha256
import os
import configuration.status_messages as status_messages
from sqlalchemy.ext.declarative import declarative_base
import psycopg2

app = FastAPI()


# Some versions of sqlalchemy do not support postgres in the url, it has to be postgresql
db_url = os.environ.get('DATABASE_URL')
if (db_url.find('postgresql') == -1):
    db_url = db_url.replace('postgres', 'postgresql')

engine = create_engine(db_url)
session = sessionmaker(engine)()
Base = declarative_base()


@app.get('/users/{username}', response_model=User)
async def read_user(username: str):
    user_dict = fake_users_db[username]
    if not user_dict:
        raise HTTPException(status_code=400, detail='User not found')
    user = User(**user_dict)
    return user


@app.get('/')
async def home():
    return status_messages.public_status_messages.get_message('hello_users')


@app.get('/pong')
async def pong():
    return status_messages.public_status_messages.get_message('pong')


@app.post('/login/')
async def login(login_data: Login):
    aux_user = session.query(db_user.User).filter(db_user.User.email == login_data.email).first()
    if ((aux_user is None) or (not pbkdf2_sha256.verify(login_data.password, aux_user.hashed_password))):
        raise HTTPException(
            status_code=400,
            detail=status_messages.public_status_messages.get_message('failed_login')[status_messages.MESSAGE_NAME_FIELD]
        )
    else:
        return status_messages.public_status_messages.get_message('successful_login')

@app.post('/admin_login/')
async def login(admin_login_data: AdminLogin):
    aux_admin = session.query(db_admin.Admin).filter(db_admin.Admin.email == admin_login_data.email).first()
    if ((aux_admin is None) or (not pbkdf2_sha256.verify(admin_login_data.password, aux_admin.hashed_password))):
        raise HTTPException(
            status_code=400,
            detail=status_messages.public_status_messages.get_message('failed_login')[status_messages.MESSAGE_NAME_FIELD]
        )
    else:
        return status_messages.public_status_messages.get_message('successful_login')

@app.post('/create/')
async def create(user_data: RegistrationData):
    # TODO: AGREGAR REGISTRO CON GOOGLE
    # TODO: CHEQUEAR QUE NO ESTE REGISTRADO NORMALMENTE O CON GOOGLE

    # https://www.psycopg.org/docs/errors.html
    # sqlalchemy.exc.IntegrityError
    # psycopg2.errors.UniqueViolation
    aux_user = db_user.User(user_data.email, user_data.password, user_data.name)

    try:
        session.add(aux_user)
        session.commit()
        return {
            **status_messages.public_status_messages.get_message('successful_registration'),
            'email': aux_user.email
            }
    except exc.IntegrityError as e:
        session.rollback()
        if isinstance(e.orig, psycopg2.errors.NotNullViolation):
            return status_messages.public_status_messages.get_message('null_value')
        elif isinstance(e.orig, psycopg2.errors.UniqueViolation):
            return status_messages.public_status_messages.get_message('existing_user')
        else:
            message = status_messages.public_status_messages.get_message('unexpected_error')
            raise HTTPException(
            status_code=message["code"],
            detail=message[status_messages.MESSAGE_NAME_FIELD]
        )
    


@app.post('/admin_create/')
async def create_admin(admin_data: AdminRegistrationData):
    aux_admin = db_admin.Admin(admin_data.email, admin_data.password, admin_data.name)

    try:
        session.add(aux_admin)
        session.commit()
        return {'status': 'ok', 'message': 'admin successfully registered',
                'user': {'email': aux_admin.email}}
    except exc.IntegrityError:
        session.rollback()
        return {'status': 'error', 'message': 'user already registered'}

@app.get('/users_list')
async def users_list():
    emails_query = session.query(db_user.User.email).all()
    emails_list = []
    for email in emails_query:
        emails_list.append(email[0])

    return_message = status_messages.public_status_messages.get_message('successful_get_users')
    return {
        **return_message,
        "users": emails_list
        }

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=int(os.environ.get('PORT')))
    
