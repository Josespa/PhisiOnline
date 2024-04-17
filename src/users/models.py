import flask
from src import db, app
from werkzeug.security import generate_password_hash, check_password_hash

additional_languages = db.Table('additional_languages',
    db.Column('language_id', db.Integer, db.ForeignKey('language.id'), primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True)
    )

class User(db.Model):
    id              =   db.Column(db.Integer, unique =True, primary_key=True)
    first_name      =   db.Column(db.String(50), nullable=False)
    last_name       =   db.Column(db.String(50), nullable=False)
    email           =   db.Column(db.String(50), unique=True, nullable=False)
    password        =   db.Column(db.String(250), nullable=False)
    user_type       =   db.Column(db.String(50), nullable=False)
    birthdate       =   db.Column(db.DateTime)
    calendarid      =   db.Column(db.String(250))
    language        =   db.Column(db.Integer, nullable=False)
    created_at      =   db.Column(db.DateTime, nullable = False)
    updated_at      =   db.Column(db.DateTime, nullable = False)
    status          =   db.Column(db.String(50), nullable = False)   
    resume          =   db.Column(db.Text) 
    image           =   db.Column(db.String(250), default = 'profile.jpg')
    #Relation to many languages for physios
    lang_additional =   db.relationship('Language', secondary=additional_languages, lazy='subquery',
        backref=db.backref('User', lazy=True))
    

    def __repr__(self):
        return f'User: {self.first_name + ' ' +self.last_name }'

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def get_password(self, password):
        return check_password_hash(self.password, password)

class Language(db.Model):
    id              =   db.Column(db.Integer, unique =True, primary_key=True)
    code            =   db.Column(db.String(5))
    title           =   db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return f'Language: {self.title}'

class Ratebyusers(db.Model):
    id              =   db.Column(db.Integer, unique =True, primary_key=True)
    value           =   db.Column(db.Integer, nullable=False)
    userid          =   db.Column(db.Integer, nullable=False)
    comments        =   db.Column(db.Text)

    def __repr__(self):
        return f'Language: {self.title}'

with app.app_context():
    db.create_all()
    #Add primary languages
    lang = Language.query.first()
    if not lang:
        try:

            lang = Language(id = 1, code = 'en_UK', title = 'English')
            db.session.add(lang)
            lang = Language(id = 2, code = 'de_DE', title = 'Deutsch')
            db.session.add(lang)
            lang = Language(id = 3, code = 'es_ES', title = 'Español')
            db.session.add(lang)
            db.session.commit()

        except TypeError as error:
            print('An error occurred: %s' % error)