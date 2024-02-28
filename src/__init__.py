from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask import render_template


# this variable, db, will be used for all SQLAlchemy commands
db = SQLAlchemy()

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
app = Flask(__name__)
app.config.from_object(Config)
app.config['UPLOAD_FOLDER'] = Config.UPLOAD_FOLDER
#app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://"+Config.UID+":"+Config.PWD+"@"+Config.SERVER+"/"+Config.DATABASE
app.config["SQLALCHEMY_DATABASE_URI"] = Config.connection_string

# initialize the app with Flask-SQLAlchemy
db.init_app(app)


from src import routes
