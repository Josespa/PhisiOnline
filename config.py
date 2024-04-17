import os
from src.database.db import connection_string

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or "secret_string"
    UPLOAD_FOLDER = 'src/static/images/'
    
    #Config Database postgresql
    connection_string_config = connection_string

    