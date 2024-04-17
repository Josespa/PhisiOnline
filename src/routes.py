import os.path
from src import app, db, ALLOWED_EXTENSIONS
from src.languages.languages import languages, languages_codes
from src.users.routes import User, Language, login, register, logout, profile, adminedit, NewLanguage, allowed_file, Ratebyusers, mytraining,check_trainings
from src.appointments.routes import Appointment, newappointment, Exercises, EditExcerciseForm, Training
from flask import render_template, request, Response, redirect, flash, url_for, session, json
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename


@app.route("/")
@app.route("/index")
def index():
    """Show index before login
        Public page"""
    return render_template("index.html", languages_codes = languages_codes)

@app.route("/home")
def home():
    """Dashboard. first page after login
    Analytics for Admin 
    -Kpis and graph"""
    if not session.get('username'):
        return redirect(url_for('index'))
    #Get language for user
    lang = Language.query.filter_by(id = session['language']).first()
    now = datetime.now() 
    today = now.strftime("%Y-%m-%d") 
    #notifications
    notifications = notifications_user()
    if session['user_type'] == 'Patient':
        list_appointments = Appointment.query.filter_by(patientid = session['user_id'], date = today, status = 'Booked', type = 'Appointment').order_by(Appointment.date).all()
    #get all the appointments for the physio order by date
    elif session['user_type'] == 'Physiotherapist':
        list_appointments = Appointment.query.filter_by(physioid = session['user_id'], date = today, status = 'Booked', type = 'Appointment').order_by(Appointment.date).all()
    else:
        list_appointments = Appointment.query.filter_by(date = today, status = 'Booked', type = 'Appointment').order_by(Appointment.date).all()

    #get physios
    physios = User.query.filter_by(user_type = 'Physiotherapist', status = 'Active').all()
    list_languages = Language.query.all()
    additional_lang = ''
    supported_lang = []
    for l in list_languages:
        if l.code in languages_codes:
            supported_lang.append(l)
        else: 
            additional_lang += l.title+','

    check_trainings()
    #Kpis
    #Number of active patients
    num_patients = User.query.filter_by(user_type = 'Patient', status = 'Active').count()
    #Last Month Appointments
    last_month= datetime.now() - timedelta(days=30)
    last_month_appointments = Appointment.query.filter(Appointment.date>=last_month,Appointment.date<=today, Appointment.type=='Appointment', Appointment.status == 'Completed').count()
    #Percentage of Attended Appointments
    total_appointments = Appointment.query.filter(Appointment.type=='Appointment').count()
    cancel_appointments = Appointment.query.filter(Appointment.type=='Appointment',Appointment.status=='Canceled').count()
    if total_appointments:
        percentage_attended_appointments = (1-cancel_appointments/total_appointments)*100
    else:
        percentage_attended_appointments = 0
    #rating by users
    number_rates = Ratebyusers.query.count()
    all_rates = Ratebyusers.query.all()
    sum_rates = 0
    if all_rates:
        for rate in all_rates:
            sum_rates += rate.value
        avg_rating = sum_rates/number_rates
    else:
        avg_rating = sum_rates
    #appointments by month
    months = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
    appointments_month = get_appointments_month()
   
    return render_template("home.html", home_menu=True, **languages[lang.code], notifications = notifications, list_appointments = list_appointments, 
                            physios = physios, list_languages=list_languages, additional_lang = additional_lang, supported_lang = supported_lang, 
                            num_patients = num_patients, last_month_appointments = last_month_appointments, percentage_attended_appointments = percentage_attended_appointments, 
                            avg_rating = avg_rating, months = months, appointments_month = appointments_month)

@app.route("/listusers/<type>")
def listusers(type):
    """Show list of users filter by type, patients or physios
    Admin can see everything
    Physio can see patients
     """
    if not session.get('username'):
        return redirect(url_for('index'))
    #Get language for user
    lang = Language.query.filter_by(id = session['language']).first()
    if session['user_type'] == 'Patient':
        return redirect(url_for('home'))
    notifications = notifications_user()
    #Get users, filter by user type
    if type == 'patients':  
        list_users   = User.query.filter_by(user_type = 'Patient').order_by(User.id).all() 
        list_patients = True
        list_physios = False
    elif type == 'physiotherapists':
        list_users   = User.query.filter_by(user_type = 'Physiotherapist').order_by(User.id).all() 
        list_patients = False
        list_physios = True
    else: 
        return redirect(url_for('home'))
    return render_template('listusers.html',listusers=True, **languages[lang.code], list_users=list_users, 
                                list_patients = list_patients, list_physios = list_physios, notifications = notifications)

@app.route("/listappointments/<type>")
def listappointments(type):
    """ show list of appoitments
    Admin can see all appointments
    Physio and Patients patients just can see appointments where some of them are participating"""
    if not session.get('username'):
        return redirect(url_for('index'))
    #Get language for user
    lang = Language.query.filter_by(id = session['language']).first()
    notifications = notifications_user()
    if type == 'all':
        all_appointments = True
        filter_appointments = False
        #If admin get all the appointments order by date
        if session['user_type'] == 'Admin':
            list_appointments = Appointment.query.filter_by(type = 'Appointment').order_by(Appointment.date).all()
        #get all the appointments for the physio order by date
        elif session['user_type'] == 'Physiotherapist':
            list_appointments = Appointment.query.filter_by(physioid = session['user_id'], type = 'Appointment').order_by(Appointment.date).all()
        else: 
            list_appointments = Appointment.query.filter_by(patientid = session['user_id'], type = 'Appointment').order_by(Appointment.date).all()
    elif type =='booked':
        all_appointments = False
        filter_appointments = True
        #If admin get all the appointments order by date
        if session['user_type'] == 'Admin':
            list_appointments = Appointment.query.filter_by(type = 'Appointment', status = 'Booked').order_by(Appointment.date).all()
        #get all the appointments for the physio order by date
        elif session['user_type'] == 'Physiotherapist':
            list_appointments = Appointment.query.filter_by(physioid = session['user_id'], type = 'Appointment', status = 'Booked').order_by(Appointment.date).all()
        else: 
            list_appointments = Appointment.query.filter_by(patientid = session['user_id'], type = 'Appointment', status = 'Booked').order_by(Appointment.date).all()
    else: 
        return redirect(url_for('home'))
    return render_template('listappointments.html',listappointments=True, **languages[lang.code], list_appointments=list_appointments, notifications=notifications, all_appointments = all_appointments, filter_appointments = filter_appointments)

@app.route("/addlanguage", methods=['POST','GET'])
def addlanguage():
    """add new additional language, this language can be added to physio additional info"""
    if not session.get('username'):
        return redirect(url_for('index'))
    #Get language for user
    lang = Language.query.filter_by(id = session['language']).first() 
    if session['user_type'] == 'Patient':
        return redirect(url_for('home'))
    notifications = notifications_user()
    form = NewLanguage()   
    if request.method == 'POST':
        #get data from form
        if form.new_language.data != '':
            language_id     = Language.query.count()
            language_id     += 1
            new_language = form.new_language.data
            language = Language(id = language_id, title = new_language)
            db.session.add(language)
            db.session.commit()
            flash(new_language+" has been added","success")
            return redirect(request.url)
    return render_template('admin/addlanguage.html',**languages[lang.code], form=form, notifications = notifications)

@app.route("/Extensionexercises")
def Extensionexercises():
    """ Show excercises filter by category = extension"""
    if not session.get('username'):
        return redirect(url_for('index'))
    #Get language for user
    lang = Language.query.filter_by(id = session['language']).first() 
    notifications = notifications_user()
    list_exercises = Exercises.query.filter_by(category = 1, language = lang.id).order_by(Exercises.id).all()
    return render_template('excercises/Extensionexercises.html', list_exercises=list_exercises, **languages[lang.code], listexercices = True, Extension = True, notifications = notifications)

@app.route("/Flexionexercises")
def Flexionexercises():
    """ Show excercises filter by category = flexion"""
    if not session.get('username'):
        return redirect(url_for('index'))
    #Get language for user
    lang = Language.query.filter_by(id = session['language']).first() 
    notifications = notifications_user()
    list_exercises = Exercises.query.filter_by(category = 2, language = lang.id).order_by(Exercises.id).all()
    return render_template('excercises/Flexionexercises.html', **languages[lang.code], list_exercises=list_exercises, listexercices = True, Flexion = True, notifications = notifications)

@app.route("/exercise/<id>", methods=['POST','GET'])
def exercise(id):
    """ Detail information about the exercise """
    if not session.get('username'):
        return redirect(url_for('index'))
    if not id.isdigit():
        return redirect(url_for('home'))
    #Get language for user
    lang = Language.query.filter_by(id = session['language']).first() 
    notifications = notifications_user()
    list_exercise = Exercises.query.filter_by(id = id, language = lang.id).first()
    if not list_exercise:
        return redirect(url_for('home'))

    return render_template('excercises/exercise.html', **languages[lang.code], list_exercise=list_exercise, listexercices = True, notifications = notifications)

@app.route("/editexercise/<id>", methods=['POST','GET'])
def editexercise(id):
    if not session.get('username'):
        return redirect(url_for('index'))
    if not id.isdigit():
        return redirect(url_for('home'))
    #Get language for user
    lang = Language.query.filter_by(id = session['language']).first() 
    notifications = notifications_user()
    list_exercise = Exercises.query.filter_by(id = id, language = lang.id).first()
    if not list_exercise:
        return redirect(url_for('home'))
    form = EditExcerciseForm(obj=list_exercise)
    if request.method == 'POST':
        form.populate_obj(list_exercise)
        if list_exercise.name != '' and list_exercise.instructions != '':
            # check if the post request has the file part
            if 'file' not in request.files:
                return redirect(request.url)
            file = request.files['file']
            #Check if the format is allowed
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                #upload file to static folder
                exerciseimage = str(list_exercise.id)+list_exercise.name+filename
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], exerciseimage))
                list_exercise.image=exerciseimage
            now = datetime.now() 
            list_exercise.updated_at = now.strftime("%Y/%m/%d, %H:%M:%S")
            db.session.commit()
            flash("Info updated","success")
        return redirect(url_for('exercise', id = id))

    return render_template("admin/editexercise.html", list_exercise=list_exercise, **languages[lang.code], form = form, notifications = notifications)

@app.route("/patient/<id>")
def patient(id):
    if not session.get('username'):
        return redirect(url_for('index'))
    user = User.query.filter_by(id = session['user_id']).first()
    if not id.isdigit():
        return redirect(url_for('home'))
    patient = User.query.filter_by(id = id).first()
    if not patient:
        return redirect(url_for('home'))
    if patient.user_type == 'Physiotherapist':
        return redirect(url_for('physiodetail', id=id))
    #Get language for user
    lang = Language.query.filter_by(id = session['language']).first()
    notifications = notifications_user()
    patient = User.query.filter_by(id = id).first()
    list_trainings = Training.query.filter_by(patientid = id, status = 'In progress').all()
    #list_trainings = Training.query.filter_by(patientid = appointment.patientid, status = 'In progress').all()
    list_exercises = Exercises.query.filter_by(language = lang.id).all()
    return render_template("users/patient.html", **languages[lang.code], list_trainings = list_trainings, list_exercises = list_exercises, patient = patient, notifications = notifications)   

@app.route("/physiodetail/<id>")
def physiodetail(id):
    if not session.get('username'):
        return redirect(url_for('index'))
    if not id.isdigit():
        return redirect(url_for('home'))
    user = User.query.filter_by(id = session['user_id']).first()
    therapist = User.query.filter_by(id = id).first()
    if not therapist:
        return redirect(url_for('home'))
    if therapist.user_type == 'Patient':
        return redirect(url_for('patient', id=id))
    #Get language for user
    lang = Language.query.filter_by(id = session['language']).first()
    notifications = notifications_user()
    physio_info = User.query.filter_by(id = id).first()
    list_languages = Language.query.all()

    return render_template("users/physio.html", **languages[lang.code], physio_info = physio_info, list_languages = list_languages)

@app.errorhandler(404) 
# inbuilt function which takes error as parameter 
def not_found(e): 
    if not session.get('username'):
        return redirect(url_for('index'))
    user = User.query.filter_by(id = session['user_id']).first()
    #Get language for user
    lang = Language.query.filter_by(id = session['language']).first()
    notifications = notifications_user()
    return render_template("404.html", **languages[lang.code], notifications = notifications) 

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

def get_appointments_month():
    """ number of appointments per month for graph """
    list_month = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    list_all_appointments = Appointment.query.filter(Appointment.status != 'Cancel',Appointment.type == 'Appointment').order_by(Appointment.date).all()
    for i in list_all_appointments:
        if i.date.strftime("%m") == "01":
            list_month[0] += 1
        if i.date.strftime("%m") == "02":
            list_month[1] += 1
        if i.date.strftime("%m") == "03":
            list_month[2] += 1
        if i.date.strftime("%m") == "04":
            list_month[3] += 1
        if i.date.strftime("%m") == "05":
            list_month[4] += 1
        if i.date.strftime("%m") == "06":
            list_month[5] += 1
        if i.date.strftime("%m") == "07":
            list_month[6] += 1
        if i.date.strftime("%m") == "08":
            list_month[7] += 1
        if i.date.strftime("%m") == "09":
            list_month[8] += 1
        if i.date.strftime("%m") == "10":
            list_month[9] += 1
        if i.date.strftime("%m") == "11":
            list_month[10] += 1
        if i.date.strftime("%m") == "12":
            list_month[11] += 1
    return list_month