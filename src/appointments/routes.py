import os.path
from src import app, db
from .forms import Appointment, Dayoff, Exercises, TimeOffForm, EditExcerciseForm,Training
from flask import render_template, request, jsonify, Response, redirect, flash, url_for, session
from datetime import datetime, timedelta
from src.users.routes import User, Language
from src.googlecalendar.googlecalendar import createevent, update_event, delete_event
from src.languages.languages import languages


#new appointment in google calendar and save the data
@app.route("/newappointment", methods=['POST','GET'])
def newappointment():
    if not session.get('username'):
        return redirect(url_for('index'))
    user = User.query.filter_by(id = session['user_id']).first()
    #Get language for user
    lang = Language.query.filter_by(id = session['language']).first()
    notifications = notifications_user()
    #get languages and physios
    list_languages = Language.query.all()
    physios = User.query.filter_by(user_type = 'Physiotherapist').order_by(User.id).all()
    
    #Time schedule
    schedule = [(1, '10:00'), (2, '11:00'), (3, '12:00'), (4, '13:00'), (5, '14:00'), (6, '15:00'), (7, '16:00')]
    
    if request.method == 'POST':
        #get data from form
        physio_id = request.form.get('select_physio')
        date = request.form.get('select_date')
        time = request.form.get('select_time')
        if physio_id != '' and date != '' and time != None:
            
            physio = User.query.filter_by(id=physio_id).first()
            appo_id = Appointment.query.count()
            appo_id += 1
            
            now = datetime.now() 
            created_at = now.strftime("%Y/%m/%d, %H:%M")
            updated_at = now.strftime("%Y/%m/%d, %H:%M")
            
            selected_time = schedule[int(time)-1][1]
            
            #convert string to datetime object
            startime = datetime.strptime(schedule[int(time)-1][1], '%H:%M')
            endtime = startime + timedelta(hours=1)

            times = {
                'starting_time':str(date)+'T'+str(startime.time()),
                'ending_time': str(date)+'T'+str(endtime.time())
            }
            #create event in google calendar
            event = createevent(physio, user, times)
            status = 'Booked'
            #if event save new appointment
            if event:
                appointment = Appointment(id=appo_id, eventid=event['id'], date = date, time = schedule[int(time)-1][1], patientid = user.id, 
                                    patientname = user.first_name + ' ' + user.last_name, physioid = physio.id, physioname = physio.first_name + ' ' + physio.last_name, 
                                    type = 'Appointment',notes = "Nothing", link = event['hangoutLink'], status = status, created_at = created_at,  updated_at = updated_at)
                
                db.session.add(appointment)
                db.session.commit()
                return redirect(url_for('appointment',id=appo_id))
            else:
                flash("Sorry, something went wrong.","danger")
        else:
            pass
    return render_template('appointments/newappointment.html', user = user, language = lang, list_languages = list_languages, physios = physios, **languages[lang.code], notifications = notifications)

@app.route("/availability",methods=["POST","GET"])
def availability():  
    """check availability for physio and date"""
    if request.method == 'POST':
        physio = request.form['physio_id'] 
        date = request.form['date'] 
        now = datetime.now() 
        today = now.strftime("%Y-%m-%d") 
        schedule = [(1, '10:00'), (2, '11:00'), (3, '12:00'), (4, '13:00'), (5, '14:00'), (6, '15:00'), (7, '16:00')]
        aux = schedule[:]
        OutputArray = []
        if date > today:
            day_off = Dayoff.query.filter_by(date=date, physioid = physio).all()
            if not day_off:
                appointments = Appointment.query.filter_by(physioid = physio, date = date,status = 'Booked').order_by(Appointment.time).all()
                if appointments: 
                    for row in schedule:
                        for app in appointments:
                            #remove time from the list if there is an appointment
                            if app.time == row[1]:
                                aux.remove((row[0],row[1]))
                                break
                                
                for row in aux:    
                    outputObj = {
                                'id': row[0],
                                'name': row[1]}
                    OutputArray.append(outputObj)  
                  
    #return updated schedule
    return jsonify(OutputArray)

#appointment detal
@app.route("/appointment/<id>", methods=['GET'])
def appointment(id):
    if not session.get('username'):
        return redirect(url_for('index'))
    if not id.isdigit():
        return redirect(url_for('home'))
    user = User.query.filter_by(id = session['user_id']).first()
    #Get language for user
    lang = Language.query.filter_by(id = session['language']).first()
    notifications = notifications_user()
    appointment = Appointment.query.filter_by(id = id).first()
    if not appointment:
        return redirect(url_for('home'))
    physio      = User.query.filter_by(id = appointment.physioid).first()
    now = datetime.now() 
    today = now.strftime("%Y-%m-%d")
    appointment_date = appointment.date.strftime("%Y-%m-%d")
    #if meeting is today, link available
    if today != appointment_date:
        appointment_date = ''

    list_trainings = Training.query.filter_by(patientid = appointment.patientid, status = 'In progress').all()
    list_exercises = Exercises.query.all()
    return render_template("appointments/appointment.html", user=user, appointment =appointment, language = lang, 
                            physio=physio, appointment_date=appointment_date, **languages[lang.code], list_trainings = list_trainings,
                            list_exercises = list_exercises, notifications = notifications)

@app.route("/editappointment/<id>", methods=['GET','POST'])
def editappointment(id):
    if not session.get('username'):
        return redirect(url_for('index'))
    if not id.isdigit():
        return redirect(url_for('home'))
    user = User.query.filter_by(id = session['user_id']).first()
    #Get language for user
    lang = Language.query.filter_by(id = session['language']).first()
    notifications = notifications_user()
    appointment = Appointment.query.filter_by(id = id).first()
    if not appointment:
        return redirect(url_for('home'))
    physios = User.query.filter_by(user_type = 'Physiotherapist').order_by(User.id).all()
    list_languages = Language.query.all()
    schedule = [(1, '10:00'), (2, '11:00'), (3, '12:00'), (4, '13:00'), (5, '14:00'), (6, '15:00'), (7, '16:00')]
    if request.method == 'POST':
        date = request.form.get('updateselect_date')
        time = request.form.get('updateselect_time')
        if date != '' and time != None:
            physio = User.query.filter_by(id=appointment.physioid).first()
            selected_time = schedule[int(time)-1][1]
            #convert string to datetime object
            startime = datetime.strptime(schedule[int(time)-1][1], '%H:%M')
            endtime = startime + timedelta(hours=1)
            times = {
                'starting_time':str(date)+'T'+str(startime.time()),
                'ending_time': str(date)+'T'+str(endtime.time())
            }
            #update event in google calendar and save updated date
            update_event(physio.calendarid, appointment.eventid, times)
            now = datetime.now() 
            updated_at = now.strftime("%Y/%m/%d, %H:%M")
            appointment.date = date
            appointment.time = schedule[int(time)-1][1]
            appointment.updated_at = updated_at
            db.session.commit()
            flash("Info updated","success")
            return redirect(url_for('appointment',id=appointment.id))
        else:
            pass
    return render_template('appointments/editappointment.html', user = user, language = lang, list_languages=list_languages, appointment=appointment,**languages[lang.code], notifications = notifications)

@app.route("/cancelappointment/<id>", methods=['GET','POST'])
def cancelappointment(id):
    if not session.get('username'):
        return redirect(url_for('index'))
    if not id.isdigit():
        return redirect(url_for('home'))
    user = User.query.filter_by(id = session['user_id']).first()
    appointment = Appointment.query.filter_by(id=id).first()
    if not appointment:
        return redirect(url_for('home'))
    physio = User.query.filter_by(id=appointment.physioid).first()
    #delete event in google calendar and change status
    delete_event(physio.calendarid, appointment.eventid)
    appointment.status = 'Canceled'
    db.session.commit()
    flash("Info updated","success")
    return redirect(url_for('appointment',id=appointment.id))

@app.route("/completeappointment/<id>", methods=['GET','POST'])
def completeappointment(id):
    if not session.get('username'):
        return redirect(url_for('index'))
    if not id.isdigit():
        return redirect(url_for('home'))
    user = User.query.filter_by(id = session['user_id']).first()
    appointment = Appointment.query.filter_by(id=id).first()
    if not appointment:
        return redirect(url_for('home'))
    physio = User.query.filter_by(id=appointment.physioid).first()
    appointment.status = 'Completed'
    db.session.commit()
    flash("Info updated","success")
    return redirect(url_for('appointment',id=appointment.id))

#time off
@app.route("/timeoff", methods=['POST','GET'])
def timeoff():
    """ Time off just for physio """
    if not session.get('username'):
        return redirect(url_for('index'))
    if session['user_type'] != 'Physiotherapist':
        return redirect(url_for('home'))
    user = User.query.filter_by(id = session['user_id']).first()
    #Get language for user
    lang = Language.query.filter_by(id = session['language']).first()
    notifications = notifications_user()
    form = TimeOffForm()
    if request.method == 'POST':
        #get data from form
        physio_id = request.form.get('select_physio')
        date = request.form.get('select_datetime_off')
        time = request.form.get('select_timeoff')
        schedule = [(1, '10:00'), (2, '11:00'), (3, '12:00'), (4, '13:00'), (5, '14:00'), (6, '15:00'), (7, '16:00')]
        if date != '' and time != None:
            appo_id = Appointment.query.count()
            appo_id += 1
            now = datetime.now() 
            created_at = now.strftime("%Y/%m/%d, %H:%M")
            updated_at = now.strftime("%Y/%m/%d, %H:%M")
            status = 'Booked'
            type = 'Time Off'
            appointment = Appointment(id=appo_id, eventid=type, date = date, time = schedule[int(time)-1][1], patientid = user.id, 
                                patientname = user.first_name + ' ' + user.last_name, physioid = user.id, physioname = user.first_name + ' ' + user.last_name, 
                                type = type,notes = type, link = type, status = status, created_at = created_at,  updated_at = updated_at)
                
            db.session.add(appointment)
            db.session.commit()
            flash("You booked time off on "+str(date) + " at "+str(schedule[int(time)-1][1]),"success")
            #return redirect(url_for('home'))
        else:
            pass
    return render_template('appointments/timeoff.html', form = form, **languages[lang.code], timeoff_sidebar = True, timeoff_dropmenu = True, notifications = notifications)

@app.route("/availability_timeoff",methods=["POST","GET"])
def availability_timeoff():  
    """check availability for physio and date"""
    if request.method == 'POST': 
        date = request.form['date'] 
        user = User.query.filter_by(id = session['user_id']).first()
        now = datetime.now() 
        today = now.strftime("%Y-%m-%d") 
        schedule = [(1, '10:00'), (2, '11:00'), (3, '12:00'), (4, '13:00'), (5, '14:00'), (6, '15:00'), (7, '16:00')]
        aux = schedule[:]
        OutputArray = []
        if date > today:
            day_off = Dayoff.query.filter_by(date=date,physioid=user.id).all()
            if not day_off:
                appointments = Appointment.query.filter_by(physioid = user.id, date = date,status = 'Booked').order_by(Appointment.time).all()
                if appointments: 
                    for row in schedule:
                        for app in appointments:
                            #remove time from the list if there is an appointment
                            if app.time == row[1]:
                                aux.remove((row[0],row[1]))
                                break
                for row in aux:    
                    outputObj = {
                                'id': row[0],
                                'name': row[1]}
                    OutputArray.append(outputObj)  

                   
    #return updated schedule
    return jsonify(OutputArray)

#time off
@app.route("/dayoff", methods=['POST','GET'])
def dayoff():
    """ Day off just for physio """
    if not session.get('username'):
        return redirect(url_for('index'))
    if session['user_type'] != 'Physiotherapist':
        return redirect(url_for('home'))
    user = User.query.filter_by(id = session['user_id']).first()
    #Get language for user
    lang = Language.query.filter_by(id = session['language']).first()
    notifications = notifications_user()
    form = TimeOffForm()
    if request.method == 'POST':
        date = request.form.get('select_date_off')
        if date != '':
            appointments =  Appointment.query.filter_by(date = date, physioid = user.id, type = 'Appointment').all()
            days_off = Dayoff.query.filter_by(date = date, physioid = user.id).all()
            if days_off:
                flash("You already have a day off on "+str(date),"danger")
            else:
                if not appointments: 
                    timeoff_id = Dayoff.query.count()
                    timeoff_id += 1
                    now = datetime.now() 
                    created_at = now.strftime("%Y/%m/%d, %H:%M")
                    updated_at = now.strftime("%Y/%m/%d, %H:%M")
                    day_off = Dayoff(id = timeoff_id, date = date, physioid = user.id, created_at = created_at, updated_at = updated_at)
                    db.session.add(day_off)
                    db.session.commit()
                    flash("You booked a day off on "+str(date),"success")
                else:
                    flash("You have appointments on "+str(date),"danger")
            #return redirect(url_for('home'))
    return render_template('appointments/dayoff.html', form = form, **languages[lang.code],timeoff_sidebar = True, dayoff_sidebar = True, notifications = notifications)

@app.route("/addtraining/<id>", methods=['POST','GET'])
def addtraining(id):
    """ Add training for patient """
    if not session.get('username'):
        return redirect(url_for('index'))
    if session['user_type'] == 'Patient':
        return redirect(url_for('home'))
    if not id.isdigit():
        return redirect(url_for('home'))
    user = User.query.filter_by(id = session['user_id']).first()
    #Get language for user
    lang = Language.query.filter_by(id = session['language']).first()
    notifications = notifications_user()
    #get patient 
    patient = User.query.filter_by(id = id).first()
    if not patient:
        return redirect(url_for('home'))
    list_exercises = Exercises.query.filter_by(language = lang.id).order_by(Exercises.id).all()
    
    if request.method == 'POST':
        #get data from form
        category_id = request.form.get('select_category')
        exercise_id = request.form.get('select_exercise')
        end_date    = request.form.get('select_endtdate')
        repetitions = request.form.get('select_repetitions')
        notes       = request.form.get('notes_training')
        if category_id != '' and exercise_id!= None and end_date != '' and repetitions != '':
            now = datetime.now() 
            start_date = now.strftime("%Y-%m-%d")
            if start_date < end_date:
                train_id = Training.query.count()
                train_id += 1
                status = 'In progress'
                #check if has same exercise in progress
                trainings = Training.query.filter_by(patientid = patient.id, exercise = exercise_id, status = status).all()
                if not trainings:
                    created_at = now.strftime("%Y/%m/%d, %H:%M")
                    updated_at = now.strftime("%Y/%m/%d, %H:%M")
                    
                    new_training = Training(id = train_id, patientid = patient.id, exercise = exercise_id,created_by = session['user_id'], 
                                                frecuency = repetitions, date_start = start_date, date_end = end_date, status = status,
                                                created_at = created_at, updated_at = updated_at)
                    db.session.add(new_training)
                    db.session.commit()
                      
                return redirect(url_for('patient',id=patient.id))
            else:
                flash("Sorry, something went wrong.","danger")    


    return render_template('excercises/addtraining.html', **languages[lang.code], patient = patient, list_exercises = list_exercises, notifications = notifications)

@app.route("/exercises_category",methods=["POST","GET"])
def exercises_category():  
    """filter exercises by category"""
    if request.method == 'POST':
        category_id = request.form['category_id'] 
        OutputArray = []
        if category_id: 
            
            #Get language for user
            lang = Language.query.filter_by(id = session['language']).first()
            #get exercises by category and language
            list_exercises = Exercises.query.filter_by(category = category_id, language = lang.id).order_by(Exercises.id).all()
            
            for exercise in  list_exercises:
                outputObj = {
                            'id': exercise.id,
                            'name': exercise.name}
                OutputArray.append(outputObj) 
            else:
                pass
                
    return jsonify(OutputArray)

def notifications_user():
    now = datetime.now() 
    today = now.strftime("%Y-%m-%d") 
    notifications = []
    #If admin get all the appointments order by date
    if session['user_type'] == 'Patient':
        list_appointments = Appointment.query.filter_by(patientid = session['user_id'], date = today).order_by(Appointment.date).all()
        notifications = list_appointments
    #get all the appointments for the physio order by date
    elif session['user_type'] == 'Physiotherapist':
        list_appointments = Appointment.query.filter_by(physioid = session['user_id'], date = today).order_by(Appointment.date).all()
        notifications = list_appointments
    
    return notifications  