from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField,SelectMultipleField,DateField
from src.appointments.models import  Appointment


class NewAppointment(FlaskForm):
    date        = DateField("Date")
    time        = SelectField(u'Time', coerce=int)
    physio      = SelectField(u'Physiotherapist', coerce=int)
    notes       = StringField("Notes")