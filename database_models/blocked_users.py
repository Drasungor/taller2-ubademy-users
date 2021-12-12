from sqlalchemy import Column, String
from passlib.hash import pbkdf2_sha256
import database_models.database_shared_constants as database_shared_constants
from database.database import Base
from passlib.pwd import genword


data_size = {
    'email': database_shared_constants.CONST_EMAIL_LENGTH,
    }


class Google(Base):
    __tablename__ = "blocked_users"

    email = Column(String(database_shared_constants.CONST_EMAIL_LENGTH), primary_key = True)

    def __init__(self, email):
        self.email = None
        if (email != ""):
            self.email = email
