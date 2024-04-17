from flask_wtf import FlaskForm
from wtforms import StringField, SelectField,DateField
from .models import Appointment, Dayoff, Exercises, Training

class TimeOffForm(FlaskForm):
    date        = DateField("Date")
    Time        = SelectField(u'Time', coerce=int)

class EditExcerciseForm(FlaskForm):
    name            = StringField("Name")
    description     = StringField("Description")
    instructions    = StringField("Instructions")
    image           = StringField("Image")

