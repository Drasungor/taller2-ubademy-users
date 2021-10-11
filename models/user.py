from pydantic import BaseModel
from typing import Optional
from sqlalchemy import Column, String


CONST_EMAIL_LENGTH = 50 #TODO: VER EL TAMANIO MAXIMO DE LOS MAILS
CONST_PASSWORD_LENGTH = 50
CONST_SALT_LENGTH = CONST_PASSWORD_LENGTH


fake_users_db = {
    "johndoe": {
        "username": "johndoe",
        "full_name": "John Doe",
        "email": "johndoe@example.com",
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
        "disabled": False,
    }
}


class User(Base):
    __tablename__ = "users"

    email = Column(Integer(String(CONST_EMAIL_LENGTH)))
    hashed_password = Column(String(CONST_PASSWORD_LENGTH))
    hash_salt = Column(String(CONST_SALT_LENGTH))
    


"""class User(BaseModel):
    username: str
    hashed_password: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    disabled: Optional[bool] = None"""

