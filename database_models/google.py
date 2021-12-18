from sqlalchemy import Column, String, Boolean, DateTime
from passlib.hash import pbkdf2_sha256
import database_models.database_shared_constants as database_shared_constants
from database.database import Base
from passlib.pwd import genword
from datetime import datetime


data_size = {
    'email': database_shared_constants.CONST_EMAIL_LENGTH,
    }


class Google(Base):
    __tablename__ = "Google"

    email = Column(String(database_shared_constants.CONST_EMAIL_LENGTH), primary_key = True)
    firebase_password = Column(String(database_shared_constants.CONST_HASH_LENGTH), nullable = False)
    is_blocked = Column(Boolean(), nullable = False)
    registration_date = Column(DateTime(), nullable = False)
    last_login_date = Column(DateTime(), nullable = False)
    expo_token = Column(String(database_shared_constants.EXPO_TOKEN_LENGTH), nullable = False)

    def __init__(self, email, is_blocked, expo_token):
        self.email = None
        self.is_blocked = None
        self.expo_token = None
        self.firebase_password = genword(charset = "hex", length = 50)
        self.registration_date = datetime.now()
        self.last_login_date = datetime.now()
        if (email != ""):
            self.email = email
        
        if (expo_token != ""):
            self.expo_token = expo_token

        if (isinstance(is_blocked, bool)):
            self.is_blocked = is_blocked

    def __print__(self):
        print("Email: " + self.email)
        print("Is blocked: " + str(self.hashed_password))