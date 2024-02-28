import os.path
from src import app, db, ALLOWED_EXTENSIONS
from src.users.routes import User, Language, login, register, logout, profile, adminedit
from src.appointments.routes import Appointment, newappointment

from flask import render_template, request, jsonify, Response, redirect, flash, url_for, session
from datetime import datetime, timedelta

from src.exercises.exercises import exercises_json
from src.languages.languages import languages

@app.route("/")
@app.route("/index")
def index():
    return render_template("index.html" )

@app.route("/home")
def home():
    if not session.get('username'):
        return redirect(url_for('index'))
    #Get language for user
    lang = Language.query.filter_by(id = session['language']).first()
    return render_template("home.html", home=True, **languages[lang.code])

@app.route('/listusers')
def listusers():
    if not session.get('username'):
        return redirect(url_for('index'))
    #Get language for user
    lang = Language.query.filter_by(id = session['language']).first()
    list_users   = User.query.order_by(User.id).all() 
    return render_template('admin/listusers.html',listusers=True, **languages[lang.code], list_users=list_users)

@app.route("/listappointments")
def listappointments():
    if not session.get('username'):
        return redirect(url_for('index'))
    #Get language for user
    lang = Language.query.filter_by(id = session['language']).first()
    #If admin get all the appointments order by date
    if session['user_type'] == 'Admin':
        list_appointments = Appointment.query.order_by(Appointment.date).all()
    #get all the appointments for the physio order by date
    elif session['user_type'] == 'Physiotherapist':
        list_appointments = Appointment.query.filter_by(physioid = session['user_id']).order_by(Appointment.date).all()
    else: 
        list_appointments = Appointment.query.filter_by(patientid = session['user_id']).order_by(Appointment.date).all()
    return render_template('listappointments.html',listappointments=True, **languages[lang.code], list_appointments=list_appointments)

@app.route('/exercises')
def exercises():
    if not session.get('username'):
        return redirect(url_for('index'))
        
    return render_template('null.html')
   
@app.errorhandler(404) 
# inbuilt function which takes error as parameter 
def not_found(e): 
    if not session.get('username'):
        return redirect(url_for('index'))
    user = User.query.filter_by(id = session['user_id']).first()
    # defining function 
    return render_template("404.html", user=user) 
