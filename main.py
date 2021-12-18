from sqlalchemy.engine import create_engine
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
from models.send_message_data import SendMessage
from models.admin_login_data import AdminLogin
from models.google_login_data import GoogleLogin
from models.block_user_data import BlockUserData
from sqlalchemy.exc import DataError
import database_models.user as db_user
import database_models.admin as db_admin
import database_models.google as db_google
from passlib.hash import pbkdf2_sha256
import os
import configuration.status_messages as status_messages
from psycopg2.errors import NotNullViolation, UniqueViolation, StringDataRightTruncation
from server_exceptions.unexpected_error import UnexpectedErrorException
from fastapi.responses import JSONResponse
from datetime import datetime

import requests

Base.metadata.create_all(engine)

app = FastAPI()


def get_db():
    db = Session()
    try:
        yield db
    finally:
        db.close()


def generate_first_admin():
    db = Session()
    aux_admin = db_admin.Admin("admin", "admin", "admin")

    try:
        db.add(aux_admin)
        db.commit()
        return True
    except exc.IntegrityError as e:
        db.rollback()
        if isinstance(e.orig, UniqueViolation):
            return True
        else:
            return False
    except Exception:
        db.rollback()
        return False




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
        return status_messages.public_status_messages.get_message('failed_login')
    elif aux_user.is_blocked:
        return status_messages.public_status_messages.get_message('user_is_blocked')
    else:
        db.query(DbUser).filter(DbUser.email == login_data.email).update({
                DbUser.last_login_date: datetime.now(),
                DbUser.expo_token: login_data.expo_token
            })
        db.commit()
        return {
            **status_messages.public_status_messages.get_message('successful_login'),
            'firebase_password': aux_user.firebase_password,
            }


@app.post('/admin_login/')
async def login(admin_login_data: AdminLogin, db: Session = Depends(get_db)):
    aux_admin = db.query(db_admin.Admin).filter(db_admin.Admin.email == admin_login_data.email).first()
    if (aux_admin is None) or (not pbkdf2_sha256.verify(admin_login_data.password, aux_admin.hashed_password)):
        return status_messages.public_status_messages.get_message('failed_login')
    else:
        return status_messages.public_status_messages.get_message('successful_login')


@app.post('/create/')
async def create(user_data: RegistrationData, db: Session = Depends(get_db)):
    # https://www.psycopg.org/docs/errors.html
    aux_user = DbUser(user_data.email, user_data.password, False, user_data.expo_token)
    google_account = db.query(db_google.Google).filter(db_google.Google.email == user_data.email).first()

    if google_account is not None:
        return status_messages.public_status_messages.get_message('has_google_account'),

    try:
        db.add(aux_user)
        db.commit()
        return {
            **status_messages.public_status_messages.get_message('successful_registration'),
            'email': aux_user.email,
            'firebase_password': aux_user.firebase_password
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


@app.get('/users_list/{is_admin}')
async def users_list(is_admin: str, db: Session = Depends(get_db)):
    if is_admin  != "true":
        return status_messages.public_status_messages.get_message('not_admin')

    users_query = db.query(DbUser.email, DbUser.is_blocked).all()
    google_users_query = db.query(db_google.Google.email, db_google.Google.is_blocked).all()
    users_list = []

    for user in users_query:
        users_list.append({"email": user[0], "is_blocked": user[1]})
    for user in google_users_query:
        users_list.append({"email": user[0], "is_blocked": user[1]})

    return {
        **status_messages.public_status_messages.get_message('successful_get_users'),
        "users": users_list
        }

@app.post('/oauth_login')
async def oauth_login(google_data: GoogleLogin, db: Session = Depends(get_db)):
    aux_account = db.query(db_user.User).filter(db_user.User.email == google_data.email).first()
    if aux_account is not None:
        return {**status_messages.public_status_messages.get_message('has_normal_account')}
    google_account = db.query(db_google.Google).filter(db_google.Google.email == google_data.email).first()

    if google_account is None:
        google_account = db_google.Google(google_data.email, False, google_data.expo_token)
        try:
            db.add(google_account)
            db.commit()
            return {
                **status_messages.public_status_messages.get_message('successful_registration'),
                'email': google_account.email,
                'firebase_password': google_account.firebase_password,
                'created': True
                }
        except exc.IntegrityError as e:
            db.rollback()
            if isinstance(e.orig, NotNullViolation):
                return status_messages.public_status_messages.get_message('null_value')
                
            else:
                raise UnexpectedErrorException
        except DataError as e:
            db.rollback()
            if isinstance(e.orig, StringDataRightTruncation):
                return {
                    **status_messages.public_status_messages.get_message('wrong_size_input'),
                    'input_sizes': db_google.data_size}
            else:
                print(e)
                raise UnexpectedErrorException
        except Exception as e:
            db.rollback()
            print(e)
            raise UnexpectedErrorException
    else:
        db.query(db_google.Google).filter(db_google.Google.email == google_data.email).update({
                db_google.Google.last_login_date: datetime.now(),
                db_google.Google.expo_token: google_data.expo_token
            })
        db.commit()
        return {
            **status_messages.public_status_messages.get_message('google_existing_account'),
            'email': google_account.email,
            'firebase_password': google_account.firebase_password, 
            'created': False
            }

@app.post('/change_blocked_status')
async def block_user(block_data: BlockUserData, db: Session = Depends(get_db)):
    try:
        aux_account = db.query(db_user.User).filter(db_user.User.email == block_data.modified_user).first()
        google_aux_account = db.query(db_google.Google).filter(db_google.Google.email == block_data.modified_user).first()
        if aux_account is not None:
            db.query(db_user.User).filter(db_user.User.email == block_data.modified_user).update({
                db_user.User.is_blocked: block_data.is_blocked
            })
            db.commit()
            return status_messages.public_status_messages.get_message('user_updated')
        elif google_aux_account is not None:
            db.query(db_google.Google).filter(db_google.Google.email == block_data.modified_user).update({
                db_google.Google.is_blocked: block_data.is_blocked
            })
            db.commit()
            return status_messages.public_status_messages.get_message('user_updated')
        else:
            return status_messages.public_status_messages.get_message('user_does_not_exist')
    except exc.IntegrityError as e:
        db.rollback()
        if isinstance(e.orig, NotNullViolation):
            return status_messages.public_status_messages.get_message('null_value')
        else:
            print(e)
            raise UnexpectedErrorException
    except Exception as e:
        db.rollback()
        print(e)
        raise UnexpectedErrorException


@app.get('/users_metrics')
async def users_metrics(db: Session = Depends(get_db)):
    users_query = db.query(DbUser.registration_date, DbUser.last_login_date, DbUser.is_blocked).all()
    google_users_query = db.query(db_google.Google.registration_date, db_google.Google.last_login_date, db_google.Google.is_blocked).all()
    users_list = []

    date_now = datetime.now()
    users_logged_last_hour = 0
    google_users_logged_last_hour = 0
    users_registered_last_day = 0
    google_users_registered_last_day = 0
    blocked_users = 0
    for user in users_query:
        if ((date_now - user[0]).total_seconds() < (24 * 3600)): #If the user registered in the last day
            users_registered_last_day += 1
        if ((date_now - user[1]).total_seconds() < 3600): #If the user logged in in the last hour
            users_logged_last_hour += 1
        if user[2]: #If the user is blocked
            blocked_users += 1
    for user in google_users_query:
        if ((date_now - user[0]).total_seconds() < (24 * 3600)): #If the user registered in the last day
            google_users_registered_last_day += 1
        if ((date_now - user[1]).total_seconds() < 3600): #If the user logged in in the last hour
            google_users_logged_last_hour += 1
        if user[2]: #If the user is blocked
            blocked_users += 1

    users_amount = len(users_query) + len(google_users_query)
    return {
        **status_messages.public_status_messages.get_message('got_metrics'),
        "users_amount": users_amount,
        "blocked_users": blocked_users,
        "non_blocked_users": users_amount - blocked_users,
        "last_registered_users": users_registered_last_day,
        "last_logged_users": users_logged_last_hour,
        "last_registered_google_users": google_users_registered_last_day,
        "last_logged_google_users": google_users_logged_last_hour
        }

@app.post('/send_message')
async def send_message(message_data: SendMessage, db: Session = Depends(get_db)):
    aux_account = db.query(db_user.User).filter(db_user.User.email == message_data.user_receiver_email).first()
    if aux_account is None:
        aux_account = db.query(db_google.Google).filter(db_google.Google.email == message_data.user_receiver_email).first()

    if aux_account is None:
        return status_messages.public_status_messages.get_message('user_does_not_exist')

    profile_json = {
        "to": aux_account.expo_token,
        "sound": 'default',
        "title": f'Message by {message_data.email}',
        "body": message_data,
    }
    profile_response = requests.post('https://exp.host/--/api/v2/push/send', json=profile_json)

    print(profile_response.status_code)
    if (profile_response.status_code != 200):
        raise UnexpectedErrorException
    print(profile_response.json())
    return profile_response.json()




if __name__ == '__main__':
    if not generate_first_admin():
        print("Error generating first admin user")
    # Base.metadata.drop_all(engine)
    uvicorn.run(app, host='0.0.0.0', port=int(os.environ.get('PORT')))
    
