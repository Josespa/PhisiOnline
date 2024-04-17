import flask
from src import db, app
from datetime import datetime
from src.exercises.exercises import exercises_json

class Appointment(db.Model):
    id          =   db.Column(db.Integer, unique =True, primary_key=True)
    date        =   db.Column(db.Date, nullable=False)
    time        =   db.Column(db.String(10), nullable=False)
    patientid   =   db.Column(db.Integer, nullable=False)
    patientname =   db.Column(db.String(40), nullable=False)
    physioid    =   db.Column(db.Integer, nullable=False)
    physioname  =   db.Column(db.String(40), nullable=False)
    type        =   db.Column(db.String(15), nullable=False)
    eventid     =   db.Column(db.String(200), nullable=False)
    link        =   db.Column(db.String(200), nullable=False)
    notes       =   db.Column(db.String(200))
    status      =   db.Column(db.String(15), nullable=False)    
    #rate            =   db.Column(db.Float)
    created_at  =   db.Column(db.DateTime, nullable = False)
    updated_at  =   db.Column(db.DateTime, nullable = False)


    def __repr__(self):
        return f'Appointment: {self.patientname + ' ' + str(self.date) + ' at ' + self.time}'

class Dayoff(db.Model):
    id          =   db.Column(db.Integer, unique =True, primary_key=True)
    date        =   db.Column(db.Date, nullable=False)
    physioid    =   db.Column(db.Integer, nullable=False)
    created_at  =   db.Column(db.DateTime, nullable = False)
    updated_at  =   db.Column(db.DateTime, nullable = False)

class Exercises(db.Model):
    id               =   db.Column(db.Integer, nullable=False)
    name             =   db.Column(db.String(100), primary_key=True, nullable=False)
    category         =   db.Column(db.Integer, nullable=False)
    category_name    =   db.Column(db.String(40))
    language         =   db.Column(db.Integer, nullable=False)
    description      =   db.Column(db.Text)
    instructions     =   db.Column(db.Text)
    image            =   db.Column(db.String(250), default='exercise.png')
    created_at       =   db.Column(db.DateTime, nullable = False)
    updated_at       =   db.Column(db.DateTime, nullable = False)

    def __repr__(self):
        return f'exercise: {self.name}'

class Training(db.Model):
    id          =   db.Column(db.Integer,unique =True, primary_key=True)
    patientid   =   db.Column(db.Integer, nullable=False)      
    exercise    =   db.Column(db.Integer, nullable=False)
    created_by  =   db.Column(db.Integer, nullable=False)
    frecuency   =   db.Column(db.Integer, nullable=False)
    date_start  =   db.Column(db.DateTime, nullable = False)
    date_end    =   db.Column(db.DateTime, nullable = False)
    notes       =   db.Column(db.Text)
    status      =   db.Column(db.String(20), nullable=False)
    created_at  =   db.Column(db.DateTime, nullable = False)
    updated_at  =   db.Column(db.DateTime, nullable = False)

    def __repr__(self):
        return f'Training: {'From '+str(self.date_start)+' to ' + str(self.date_end)}'

with app.app_context():
    db.create_all()
    exercises = Exercises.query.all()
    
    if not exercises:
        try:
            now = datetime.now() 
            for ex_json in exercises_json:
                exercise = Exercises(id = ex_json['id'], category =  ex_json['category'],
                        category_name=ex_json['category_name'], language = ex_json['language'],
                        name = ex_json['name'], description = ex_json['description'], 
                        instructions = ex_json['instructions'], 
                        created_at = now.strftime("%Y/%m/%d, %H:%M:%S"), updated_at = now.strftime("%Y/%m/%d, %H:%M:%S"))
                db.session.add(exercise)
                
                db.session.commit()
                #print(exercise)
        except TypeError as error:
            print('An error occurred: %s' % error)
    
    