from sqlalchemy import Column, String
from passlib.hash import pbkdf2_sha256
import database_models.database_shared_constants as database_shared_constants
from database.database import Base


data_size = {
    'email': database_shared_constants.CONST_EMAIL_LENGTH,
    }


class User(Base):
    __tablename__ = "users"

    email = Column(String(database_shared_constants.CONST_EMAIL_LENGTH), primary_key = True)
    hashed_password = Column(String(database_shared_constants.CONST_HASH_LENGTH), nullable = False)

    def __init__(self, email, password):
        self.email = None
        self.hashed_password = None
        if (email != ""):
            self.email = email

        if (password != ""):
            self.hashed_password = pbkdf2_sha256.hash(password)
