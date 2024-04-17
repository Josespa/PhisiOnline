from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField,DateField,TextAreaField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from .models import User, Language, Ratebyusers

class LoginForm(FlaskForm):
    email       = StringField("Email", validators=[DataRequired(), Email()] )
    password    = PasswordField("Password", validators=[DataRequired(), Length(min=4,max=15)])
    remember_me = BooleanField("Remember Me")
    submit      = SubmitField("Login")

class RegisterForm(FlaskForm):
    email               = StringField("Email", validators=[DataRequired()])
    password            = PasswordField("Password", validators=[DataRequired(), Length(min=4,max=15)])
    password_confirm    = PasswordField("Confirm Password", validators=[DataRequired(),Length(min=4,max=15), EqualTo('password')])
    first_name          = StringField("First Name", validators=[DataRequired(),Length(min=2,max=55)])
    last_name           = StringField("Last Name", validators=[DataRequired(),Length(min=2,max=55)])
    submit              = SubmitField("Register")

    def validate_email(self,email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError("Email is already in use. Pick another one.")

class UpdatinguserForm(FlaskForm):
    email       = StringField("Email", validators=[DataRequired()])
    first_name  = StringField("First Name", validators=[DataRequired(),Length(min=2,max=55)])
    last_name   = StringField("Last Name", validators=[DataRequired(),Length(min=2,max=55)])
    language    = SelectField(u'Language', choices=[('1', 'English'), ('2', 'Deutsch'), ('3', 'Español')])
    birthdate    = DateField("Birthday")
    add_language = SelectField(u'Additional language', coerce=int)
    resume      = TextAreaField("Resume")
    submit      = SubmitField("Update")

class UploadphotoForm(FlaskForm):
    image = StringField("Image")

class AdminUpdateUser(FlaskForm):
    language    = SelectField(u'Language', choices=[('1', 'English'), ('2', 'Deutsch'), ('3', 'Español')])
    user_type   = SelectField(u'User type', choices=[('Patient', 'Patient'), ('Physiotherapist', 'Physiotherapist')])
    status      = SelectField(u'Status', choices=[('Active', 'Active'), ('Inactive', 'Inactive')])

class NewLanguage(FlaskForm):
    new_language    = StringField("New language")
   