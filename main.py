import uvicorn
from fastapi import FastAPI, Request, Depends, HTTPException
from sqlalchemy import exc
from sqlalchemy.orm import Session

from database_models.user import User as DbUser
from database.database import Base, Session, engine
from models.user import User, fake_users_db
from models.login_data import Login
from models.registration_data import RegistrationData
from models.admin_registration_data import AdminRegistrationData
from models.admin_login_data import AdminLogin
from sqlalchemy.exc import DataError
import database_models.user as db_user
import database_models.admin as db_admin
from passlib.hash import pbkdf2_sha256
import os
import configuration.status_messages as status_messages
from psycopg2.errors import NotNullViolation, UniqueViolation, StringDataRightTruncation
from server_exceptions.unexpected_error import UnexpectedErrorException
from fastapi.responses import JSONResponse

API_KEY = 'db927b6105712695971a38fa593db084d95f86f68a1f85030ff5326d7a30c673'

Base.metadata.create_all(engine)

app = FastAPI()


def get_db():
    db = Session()
    try:
        yield db
    finally:
        db.close()


@app.middleware("http")
async def verify_api_key(request: Request, _call_next):
    authorization = request.headers['Authorization']
    if authorization != API_KEY:
        message = status_messages.public_status_messages.get_message('unauthorized_api_key')
        return JSONResponse(
            status_code=200,
            content=message
        )


@app.exception_handler(UnexpectedErrorException)
async def invalid_credentials_exception_handler(_request: Request,
                                                _exc: UnexpectedErrorException):
    message = status_messages.public_status_messages.get_message('unexpected_error')
    return JSONResponse(
        status_code=420,
        content=message
    )


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
        # TODO: ESTO NO TIENE QUE SER UNA RESPUESTA CON 400
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
    aux_user = DbUser(user_data.email, user_data.password)

    try:
        db.add(aux_user)
        db.commit()
        return {
            **status_messages.public_status_messages.get_message('successful_registration'),
            'email': aux_user.email,
            }
    except exc.IntegrityError as e:
        db.rollback()
        if isinstance(e.orig, NotNullViolation):
            return status_messages.public_status_messages.get_message('null_value')
        elif isinstance(e.orig, UniqueViolation):
            return status_messages.public_status_messages.get_message('existing_user')
        else:
            raise UnexpectedErrorException
    except DataError as e:
        db.rollback()
        if isinstance(e.orig, StringDataRightTruncation):
            return {
                **status_messages.public_status_messages.get_message('wrong_size_input'),
                'input_sizes': db_user.data_size}
        else:
            raise UnexpectedErrorException
    except Exception:
        db.rollback()
        raise UnexpectedErrorException
    

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
        if isinstance(e.orig, NotNullViolation):
            return status_messages.public_status_messages.get_message('null_value')
        elif isinstance(e.orig, UniqueViolation):
            return status_messages.public_status_messages.get_message('existing_user')
        else:
            raise UnexpectedErrorException
    except DataError as e:
        db.rollback()
        if isinstance(e.orig, StringDataRightTruncation):
            return {
                **status_messages.public_status_messages.get_message('wrong_size_input'),
                'input_sizes': db_admin.data_size}
        else:
            raise UnexpectedErrorException
    except Exception:
        db.rollback()
        raise UnexpectedErrorException


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
    
