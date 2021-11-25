import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from time import sleep

#TODO: VOLAR ESTO, METER EL COMANDO DE BASH DE GONZA PARA QUE SE SINCRONICEN BIEN LOS CONTAINERS DE DOCKER
sleep(2)

db_url = os.environ.get('DATABASE_URL', 'sqlite:///./test.db')
# Some versions of sqlalchemy do not support postgres in the url, it has to be postgresql
if db_url.find('postgresql') == -1:
    db_url = db_url.replace('postgres', 'postgresql', 1)

engine_args = {"check_same_thread": False} if 'sqlite' in db_url else {}
engine = create_engine(db_url, connect_args=engine_args)

session_args = {'bind': engine}
if 'sqlite' in db_url:
    session_args['autoflush'] = False

Session = sessionmaker(**session_args)
Base = declarative_base()
