import os
from src.database.db import SERVER,DATABASE,UID,PWD

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or "secret_string"
    UPLOAD_FOLDER = 'src/static/images/'
    
    #Config Database postgresql
    connection_string = "postgresql://"+UID+":"+PWD+"@"+SERVER+"/"+DATABASE

    