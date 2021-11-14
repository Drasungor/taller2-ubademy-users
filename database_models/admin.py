from sqlalchemy import Column, String
from sqlalchemy.ext.declarative import declarative_base
from passlib.hash import pbkdf2_sha256
import database_models.database_shared_constants as database_shared_constants

Base = declarative_base()


data_size = {
    'email': database_shared_constants.CONST_EMAIL_LENGTH,
    'name': database_shared_constants.CONST_NAME_LENGTH,
    "hashed password": database_shared_constants.CONST_HASH_LENGTH
    }


class Admin(Base):
    __tablename__ = "admins"

    email = Column(String(database_shared_constants.CONST_EMAIL_LENGTH), primary_key = True)
    hashed_password = Column(String(database_shared_constants.CONST_HASH_LENGTH), nullable = False)
    name = Column(String(database_shared_constants.CONST_NAME_LENGTH), nullable = False)

    def __init__(self, email, password, name):
        self.email = None
        self.name = None
        self.hashed_password = None
        if (email != ""):
            self.email = email

        if (password != ""):
            self.hashed_password = pbkdf2_sha256.hash(password)

        if (name != ""):
            self.name = name