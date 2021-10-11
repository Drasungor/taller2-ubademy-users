import uvicorn

from fastapi import FastAPI, HTTPException

from models.user import User, fake_users_db
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import database_models.User as db_user
from passlib.hash import pbkdf2_sha256
import os


app = FastAPI()
#engine = create_engine(process.env.DATABASE_URL)
#engine = create_engine(os.environ['DATABASE_URL'])
#engine = create_engine(DATABASE_URL)
#engine = create_engine("${DATABASE_URL}")
engine = create_engine(os.environ.get('DATABASE_URL'))
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


@app.get('/login/{email}/{password}')
async def login(email: str, password: str):
    aux_user = session.query(db_user.User).filter(db_user.User.email == email).first()
    #print(f"email:{aux_user.email} hash:{aux_user.hashed_password} name:{aux_user.name}")
    if (aux_user == None):
        raise HTTPException(status_code=400, detail='User not found')
    if (pbkdf2_sha256.verify(password, aux_user.hashed_password)):
        return {'message': 'Correct user and password'}
    else:
        return {'message': 'Incorrect password'}



if __name__ == '__main__':
    #Crea la base de datos y le mete un usuario hardcodeado
    
    """
    #db_user.Base.metadata.create_all(engine)
    session.add(db_user.User(email = "un_mail_random@gmail.com", password = "una_contrasenia", name = "Larry"))
    session.commit()
    aux_user = session.query(db_user.User).first()
    print(f"email:{aux_user.email} hash:{aux_user.hashed_password} name:{aux_user.name}")
    """
    """
    aux_user = session.query(db_user.User).first()
    print(f"email:{aux_user.email} hash:{aux_user.hashed_password} name:{aux_user.name}")
    """
    uvicorn.run(app, host='0.0.0.0', port=8001)
