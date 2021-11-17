import os
import psycopg2
import uvicorn
from fastapi import FastAPI, Depends, HTTPException
from passlib.hash import pbkdf2_sha256
from sqlalchemy import exc
from sqlalchemy.orm import Session

import database_models.admin as db_admin
import configuration.status_messages as status_messages
from database_models.user import User as DbUser
from database.database import Base, Session, engine
from models.user import User, fake_users_db
from models.login_data import Login
from models.registration_data import RegistrationData
from models.admin_registration_data import AdminRegistrationData
from models.admin_login_data import AdminLogin

Base.metadata.create_all(engine)

app = FastAPI()


def get_db():
    db = Session()
    try:
        yield db
    finally:
        db.close()


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
async def login(login_data: Login, db: Session = Depends(get_db)):
    aux_user = db.query(DbUser).filter(DbUser.email == login_data.email).first()
    if (aux_user is None) or (not pbkdf2_sha256.verify(login_data.password, aux_user.hashed_password)):
        raise HTTPException(
            status_code=400,
            detail=status_messages.public_status_messages.get_message('failed_login')[status_messages.MESSAGE_NAME_FIELD]
        )
    else:
        return status_messages.public_status_messages.get_message('successful_login')


@app.post('/admin_login/')
async def login(admin_login_data: AdminLogin, db: Session = Depends(get_db)):
    aux_admin = db.query(db_admin.Admin).filter(db_admin.Admin.email == admin_login_data.email).first()
    if (aux_admin is None) or (not pbkdf2_sha256.verify(admin_login_data.password, aux_admin.hashed_password)):
        raise HTTPException(
            status_code=400,
            detail=status_messages.public_status_messages.get_message('failed_login')[status_messages.MESSAGE_NAME_FIELD]
        )
    else:
        return status_messages.public_status_messages.get_message('successful_login')


@app.post('/create/')
async def create(user_data: RegistrationData, db: Session = Depends(get_db)):
    # TODO: AGREGAR REGISTRO CON GOOGLE
    # TODO: CHEQUEAR QUE NO ESTE REGISTRADO NORMALMENTE O CON GOOGLE

    # https://www.psycopg.org/docs/errors.html
    # sqlalchemy.exc.IntegrityError
    # psycopg2.errors.UniqueViolation
    aux_user = DbUser(user_data.email, user_data.password, user_data.name)

    try:
        db.add(aux_user)
        db.commit()
        return {
            **status_messages.public_status_messages.get_message('successful_registration'),
            'email': aux_user.email,
            'name': aux_user.name
            }
    except exc.IntegrityError as e:
        db.rollback()
        if isinstance(e.orig, psycopg2.errors.NotNullViolation):
            return status_messages.public_status_messages.get_message('null_value')
        elif isinstance(e.orig, psycopg2.errors.UniqueViolation):
            return status_messages.public_status_messages.get_message('existing_user')
        else:
            message = status_messages.public_status_messages.get_message('unexpected_error')
            # TODO: AGREGAR KEYWORD EN EL ARCHIVO PARA CODE COMO LO ES status_messages.MESSAGE_NAME_FIELD
            raise HTTPException(
                status_code=message["code"],
                detail=message[status_messages.MESSAGE_NAME_FIELD]
            )
    

@app.post('/admin_create/')
async def create_admin(admin_data: AdminRegistrationData, db: Session = Depends(get_db)):
    aux_admin = db_admin.Admin(admin_data.email, admin_data.password, admin_data.name)

    try:
        db.add(aux_admin)
        db.commit()
        return {
            **status_messages.public_status_messages.get_message('successful_registration'),
            'email': aux_admin.email,
            'name': aux_admin.name
            }
    except exc.IntegrityError as e:
        db.rollback()
        if isinstance(e.orig, psycopg2.errors.NotNullViolation):
            return status_messages.public_status_messages.get_message('null_value')
        elif isinstance(e.orig, psycopg2.errors.UniqueViolation):
            return status_messages.public_status_messages.get_message('existing_user')
        else:
            message = status_messages.public_status_messages.get_message('unexpected_error')
            # TODO: AGREGAR KEYWORD EN EL ARCHIVO PARA CODE COMO LO ES status_messages.MESSAGE_NAME_FIELD
            raise HTTPException(
                status_code=message["code"],
                detail=message[status_messages.MESSAGE_NAME_FIELD]
            )


@app.get('/users_list')
async def users_list(db: Session = Depends(get_db)):
    emails_query = db.query(DbUser.email).all()
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
    
