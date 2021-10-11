from pydantic import BaseModel
from typing import Optional
from sqlalchemy import Column, String
from sqlalchemy.ext.declarative import declarative_base
from passlib.hash import pbkdf2_sha256


CONST_EMAIL_LENGTH = 100 #TODO: VER EL TAMANIO MAXIMO DE LOS MAILS
CONST_HASH_LENGTH = 250
CONST_NAME_LENGTH = 40


class User(Base):
    __tablename__ = "users"

    email = Column(String(CONST_EMAIL_LENGTH), primary_key = True)
    hashed_password = Column(String(CONST_HASH_LENGTH))
    name = Column(String(CONST_NAME_LENGTH))
    #TODO: VER COMO METERIAMOS LO DEL USUARIO FEDERADO

    def __init__(self, email, password):
        self.email = email
        self.hashed_password = pbkdf2_sha256.hash(password)



"""

fake_users_db = {
    "johndoe": {
        "username": "johndoe",
        "full_name": "John Doe",
        "email": "johndoe@example.com",
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
        "disabled": False,
    }
}




class User(BaseModel):
    username: str
    hashed_password: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    disabled: Optional[bool] = None
    
"""

