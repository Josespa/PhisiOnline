import os.path
from src import app, db
from .models import Appointment
from .forms import NewAppointment
from flask import render_template, request, jsonify, Response, redirect, flash, url_for, session
from datetime import datetime, timedelta
from src.users.routes import User, Language
from src.googlecalendar.googlecalendar import getevents, createevent, update_event, delete_event
from src.languages.languages import languages

#new appointment in google calendar and save the data
@app.route("/newappointment", methods=['POST','GET'])
def newappointment():
    if not session.get('username'):
        return redirect(url_for('index'))
    user = User.query.filter_by(id = session['user_id']).first()
    #Get language for user
    lang = Language.query.filter_by(id = session['language']).first()
    #get languages and physios
    list_languages = Language.query.all()
    physios = User.query.filter_by(user_type = 'Physiotherapist').order_by(User.id).all()
    
    #Time schedule
    schedule = [(1, '10:00'), (2, '11:00'), (3, '12:00'), (4, '13:00'), (5, '14:00'), (6, '15:00'), (7, '16:00')]
    #form.time.choices = schedule
    if request.method == 'POST':
        #get data from from
        physio_id = request.form.get('select_physio')
        date = request.form.get('select_date')
        time = request.form.get('select_time')

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
                                notes = "Nothing", link = event['hangoutLink'], status = status, created_at = created_at,  updated_at = updated_at)
            
            db.session.add(appointment)
            db.session.commit()
            return redirect(url_for('appointment',id=appo_id))
        else:
            flash("Sorry, something went wrong.","danger")
    return render_template('appointments/newappointment.html', user = user, language = lang, list_languages = list_languages, physios = physios, **languages[lang.code])

@app.route("/availability",methods=["POST","GET"])
def availability():  
    #check availability for physio and date
    if request.method == 'POST':
        physio = request.form['physio_id'] 
        date = request.form['date'] 
        schedule = [(1, '10:00'), (2, '11:00'), (3, '12:00'), (4, '13:00'), (5, '14:00'), (6, '15:00'), (7, '16:00')]
        appointments = Appointment.query.filter_by(physioid = physio, date = date).order_by(Appointment.time).all()
        OutputArray = []
        if appointments: 
            for row in schedule:
                for app in appointments:
                    #remove time from the list if there is an appointment
                    if app.time == row[1]:
                        schedule.remove((row[0],row[1]))
                        break
                        
        for row in schedule:    
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
    user = User.query.filter_by(id = session['user_id']).first()
    #Get language for user
    lang = Language.query.filter_by(id = session['language']).first()
    appointment = Appointment.query.filter_by(id = id).first()
    physio      = User.query.filter_by(id = appointment.physioid).first()
    now = datetime.now() 
    today = now.strftime("%Y-%m-%d")
    appointment_date = appointment.date.strftime("%Y-%m-%d")
    #if meeting is today, link available
    if today != appointment_date:
        appointment_date = ''
    return render_template("appointments/appointment.html", user=user, appointment =appointment, language = lang, physio=physio, appointment_date=appointment_date, **languages[lang.code])

@app.route("/editappointment/<id>", methods=['GET','POST'])
def editappointment(id):
    if not session.get('username'):
        return redirect(url_for('index'))
    user = User.query.filter_by(id = session['user_id']).first()
    #Get language for user
    lang = Language.query.filter_by(id = session['language']).first()
    appointment = Appointment.query.filter_by(id = id).first()
    physios = User.query.filter_by(user_type = 'Physiotherapist').order_by(User.id).all()
    list_languages = Language.query.all()
    schedule = [(1, '10:00'), (2, '11:00'), (3, '12:00'), (4, '13:00'), (5, '14:00'), (6, '15:00'), (7, '16:00')]
    if request.method == 'POST':
        date = request.form.get('updateselect_date')
        time = request.form.get('updateselect_time')
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
        return redirect(url_for('appointment',id=appointment.id))
    return render_template('appointments/editappointment.html', user = user, language = lang, list_languages=list_languages, appointment=appointment,**languages[lang.code])

@app.route("/cancelappointment/<id>", methods=['GET','POST'])
def cancelappointment(id):
    if not session.get('username'):
        return redirect(url_for('index'))
    user = User.query.filter_by(id = session['user_id']).first()
    appointment = Appointment.query.filter_by(id=id).first()
    physio = User.query.filter_by(id=appointment.physioid).first()
    #delete event in google calendar and change status
    delete_event(physio.calendarid, appointment.eventid)
    appointment.status = 'Canceled'
    db.session.commit()
    return redirect(url_for('appointment',id=appointment.id))