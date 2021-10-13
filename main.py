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
    return {'message': 'Hello users!'}


@app.get('/pong')
async def pong():
    return {'message': 'pong'}


#curl https://ubademy-users-backend.herokuapp.com/login/un_mail_random@gmail.com/una_contrasenia
#curl --header "Content-Type: application/json" --request POST --data '{"email":"un_mail_random@gmail.com","password":"una_contrasenia"}' http://localhost:8003/login/

@app.post('/login/')
async def login(login_data: Login):
    aux_user = session.query(db_user.User).filter(db_user.User.email == login_data.email).first()
    #print(f"email:{aux_user.email} hash:{aux_user.hashed_password} name:{aux_user.name}")
    if (aux_user == None):
        raise HTTPException(status_code=400, detail='User not found')
    if (pbkdf2_sha256.verify(login_data.password, aux_user.hashed_password)):
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
    uvicorn.run(app, host='0.0.0.0', port=int(os.environ.get('BACKEND_USERS_PORT')))
