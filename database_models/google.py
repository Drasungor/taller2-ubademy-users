from sqlalchemy import Column, String
from passlib.hash import pbkdf2_sha256
import database_models.database_shared_constants as database_shared_constants
from database.database import Base
from passlib.pwd import genword


data_size = {
    'email': database_shared_constants.CONST_EMAIL_LENGTH,
    }


class Google(Base):
    __tablename__ = "Google"

    email = Column(String(database_shared_constants.CONST_EMAIL_LENGTH), primary_key = True)
    firebase_password = Column(String(database_shared_constants.CONST_HASH_LENGTH), nullable = False)

    def __init__(self, email):
        self.email = None
        self.firebase_password = genword(charset = "hex", length = 50)
        if (email != ""):
            self.email = email
