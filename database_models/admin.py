from sqlalchemy import Column, String
from sqlalchemy.ext.declarative import declarative_base
from passlib.hash import pbkdf2_sha256
import database_models.database_shared_constants as database_shared_constants

Base = declarative_base()

class Admin(Base):
    __tablename__ = "admins"

    username = Column(String(database_shared_constants.CONST_NAME_LENGTH), primary_key = True)
    email = Column(String(database_shared_constants.CONST_EMAIL_LENGTH), nullable = False)
    hashed_password = Column(String(database_shared_constants.CONST_HASH_LENGTH), nullable = False)
    name = Column(String(database_shared_constants.CONST_NAME_LENGTH), nullable = False)

    def __init__(self, username, email, password, name):
        self.username = None
        self.email = None
        self.name = None
        self.hashed_password = None
        if (email != ""):
            self.email = email

        if (password != ""):
            self.hashed_password = pbkdf2_sha256.hash(password)

        if (name != ""):
            self.name = name

        if (username != ""):
            self.username = username