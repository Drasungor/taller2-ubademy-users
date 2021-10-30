import uvicorn

from fastapi import FastAPI, HTTPException

from models.user import User, fake_users_db
from models.login_data import Login
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import database_models.User as db_user
from passlib.hash import pbkdf2_sha256
import os
import configuration.status_messages as status_messages

app = FastAPI()


#Some versions of sqlalchemy do not support postgres in the url, it has to be postgresql
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
    return status_messages.public_status_messages.get_message('hello_users')


@app.get('/pong')
async def pong():
    return status_messages.public_status_messages.get_message('pong')


@app.post('/login/')
async def login(login_data: Login):
    aux_user = session.query(db_user.User).filter(db_user.User.email == login_data.email).first()
    if ((aux_user == None) or (not pbkdf2_sha256.verify(login_data.password, aux_user.hashed_password))):
        raise HTTPException(status_code=400, detail= status_messages.public_status_messages.get_message('failed_login')[status_messages.MESSAGE_NAME_FIELD])
    else:
        return status_messages.public_status_messages.get_message('successful_login')


if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=int(os.environ.get('PORT')))
