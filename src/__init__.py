from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from os import environ

# this variable, db, will be used for all SQLAlchemy commands
db = SQLAlchemy()

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)
app.config.from_object(Config)
app.config['UPLOAD_FOLDER'] = Config.UPLOAD_FOLDER

#DB local
app.config["SQLALCHEMY_DATABASE_URI"] = Config.connection_string_config

#run in docker
#app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('DB_URL')

# initialize the app with Flask-SQLAlchemy
db.init_app(app)



from src import routes
