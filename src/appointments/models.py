import flask
from src import db, app

class Appointment(db.Model):
    id          =   db.Column(db.Integer, unique =True, primary_key=True)
    date        =   db.Column(db.Date, nullable=False)
    time        =   db.Column(db.String(10), nullable=False)
    patientid   =   db.Column(db.Integer, nullable=False)
    patientname =   db.Column(db.String(40), nullable=False)
    physioid    =   db.Column(db.Integer, nullable=False)
    physioname  =   db.Column(db.String(40), nullable=False)
    eventid     =   db.Column(db.String(200), nullable=False)
    link        =   db.Column(db.String(200), nullable=False)
    notes       =   db.Column(db.String(200))
    status      =   db.Column(db.String(15), nullable=False)    
    created_at  =   db.Column(db.DateTime, nullable = False)
    updated_at  =   db.Column(db.DateTime, nullable = False)


    def __repr__(self):
        return f'Appointment: {self.patientname + ' ' + str(self.date) + ' at ' + self.time}'

with app.app_context():
    db.create_all()
    