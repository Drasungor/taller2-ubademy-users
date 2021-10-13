from sqlalchemy import Column, String
from sqlalchemy.ext.declarative import declarative_base
from passlib.hash import pbkdf2_sha256


CONST_EMAIL_LENGTH = 100 #TODO: VER EL TAMANIO MAXIMO DE LOS MAILS
CONST_HASH_LENGTH = 250
CONST_NAME_LENGTH = 40

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    email = Column(String(CONST_EMAIL_LENGTH), primary_key = True)
    hashed_password = Column(String(CONST_HASH_LENGTH), nullable = False)
    name = Column(String(CONST_NAME_LENGTH), nullable = False)
    #TODO: VER COMO METERIAMOS LO DEL USUARIO FEDERADO

    def __init__(self, email, password, name):
        if (email != ""):
            self.email = email

        if (password != ""):
            self.hashed_password = pbkdf2_sha256.hash(password)

        if (name != ""):
            self.name = name
