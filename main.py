import uvicorn

from fastapi import FastAPI, HTTPException

from models.user import User, fake_users_db
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import database_models.User as db_user

app = FastAPI()
engine = create_engine("postgres://pwmutypretbutp:e74306821a303bd574c10c1444dc22cd053edcc139d06b53fd5f457b1df725eb@ec2-34-199-15-136.compute-1.amazonaws.com:5432/df3a67v8n8bo9b")
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


@app.get('/login/')
async def login(email: str, password: str):
    aux_user = session.query(db_user.User).filter(db_user.User.email == email).first()
    print(f"email:{aux_user.email} hash:{aux_user.hashed_password} name:{aux_user.name}")
    return {'message': 'aaaaaa'}



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
