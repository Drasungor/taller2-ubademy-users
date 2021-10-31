import uvicorn

from fastapi import FastAPI, HTTPException

from models.user import User, fake_users_db
from models.login_data import Login
from models.registration_data import RegistrationData
from sqlalchemy import create_engine, exc
from sqlalchemy.orm import sessionmaker
import database_models.user as db_user
from passlib.hash import pbkdf2_sha256
import os


app = FastAPI()


# Some versions of sqlalchemy do not support postgres in the url, it has to be postgresql
db_url = os.environ.get('DATABASE_URL')
if (db_url.find('postgresql') == -1):
    db_url = db_url.replace('postgres', 'postgresql')

engine = create_engine(db_url)
session = sessionmaker(engine)()


@app.get('/users/{username}', response_model=User)
async def read_user(username: str):
    user_dict = fake_users_db[username]
    if not user_dict:
        raise HTTPException(status_code=400, detail='User not found')
    user = User(**user_dict)
    return user


@app.get('/')
async def home():
    return {'message': 'Hello users!'}


@app.get('/pong')
async def pong():
    return {'message': 'pong'}


@app.post('/login/')
async def login(login_data: Login):
    aux_user = session.query(db_user.User).filter(db_user.User.email == login_data.email).first()
    if aux_user is None:
        raise HTTPException(status_code=400, detail='User not found')
    if (pbkdf2_sha256.verify(login_data.password, aux_user.hashed_password)):
        return {'message': 'Correct user and password'}
    else:
        return {'message': 'Incorrect password'}


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
        return {'status': 'ok', 'message': 'user successfully registered',
                'user': {'email': aux_user.email, 'password': aux_user.hashed_password}}
    except exc.IntegrityError:
        return {'status': 'error', 'message': 'user already registered'}

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=int(os.environ.get('PORT')))
