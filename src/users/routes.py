import os.path
from src import app, db, ALLOWED_EXTENSIONS
from .forms import User,Language, LoginForm, RegisterForm, UpdatinguserForm,UploadphotoForm, AdminUpdateUser, NewLanguage, Ratebyusers
from flask import render_template, request, jsonify, Response, redirect, flash, url_for, session
from datetime import datetime
from werkzeug.utils import secure_filename
from src.googlecalendar.googlecalendar import createcalendar, auth_googlecalendar
from src.languages.languages import languages
from src.appointments.routes import Appointment, Exercises, Training

#Login 
@app.route("/login", methods=['GET','POST'])
def login():
    if session.get('username'):
        return redirect(url_for('home'))
    form = LoginForm()
    #Validation for email and password
    if form.validate_on_submit():
        email       = form.email.data
        password    = form.password.data
        user = User.query.filter_by(email=email).first()
        #if user exist use session 
        if user and user.get_password(password):
            session['user_id'] = user.id
            session['username'] = user.first_name
            session['user_type'] = user.user_type
            session['image'] = user.image
            session['language'] = user.language
            return redirect("/home")
        else:
            flash("Sorry, something went wrong.","danger")
    return render_template("users/login.html",title="Login", form=form, login=True )

#Logout 
@app.route("/logout")
def logout():
    session['user_id'] = False
    session.pop('username',None)
    session['user_type'] = False
    session['image'] = False
    session['language'] =False
    return redirect(url_for('index'))
#New user
@app.route("/register", methods=['POST','GET'])
def register():
    if session.get('username'):
        return redirect(url_for('home'))
    form = RegisterForm()
    #Validation for email and password
    if form.validate_on_submit():
        user_id     = User.query.count()
        user_id     += 1
        email       = form.email.data
        password    = form.password.data
        first_name  = form.first_name.data
        last_name   = form.last_name.data
        #First time is always for patients 
        user_type   = 'Patient'
        status      = 'Active'
        language    = 1
        # current date and time
        now = datetime.now() 
        DateTime = now.strftime("%Y/%m/%d, %H:%M:%S")
        user = User(id=user_id, first_name=first_name, last_name=last_name, email=email, user_type = user_type, birthdate = DateTime, created_at = DateTime, updated_at = DateTime, status = status, language=language)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash("You are successfully registered!","success")
        return redirect(url_for('login'))
    return render_template("users/register.html", form=form)

#Data profile
@app.route("/profile", methods=['GET','POST'])
def profile():
    if not session.get('username'):
        return redirect(url_for('index'))
    user = User.query.filter_by(id = session['user_id']).first()
    #Get language for user
    lang = Language.query.filter_by(id = session['language']).first()
    notifications = notifications_user()
    return render_template("users/profile.html", user=user, language = lang, **languages[lang.code], notifications = notifications)

@app.route("/updateprofile", methods=['POST','GET'])
def edituser():
    if not session.get('username'):
        return redirect(url_for('index'))
    user = User.query.filter_by(id = session['user_id']).first()
    #Get language for user
    lang = Language.query.filter_by(id = session['language']).first()
    notifications = notifications_user()
    
    #fill form with user data
    form = UpdatinguserForm(obj=user)
    
    if request.method == 'POST':
        form.populate_obj(user)
        # check if the post request has the file part
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        #Check if the format is allowed
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            #upload file to static folder
            profileimage = str(user.id)+user.first_name+filename
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], profileimage))
            user.image=profileimage
        #update session
        session['username'] = user.first_name   
        session['image'] = user.image 
        session['language'] = user.language
        now = datetime.now() 
        #save last update data
        user.updated_at = now.strftime("%Y/%m/%d, %H:%M:%S")
        
        #Remove additional language if update to primary
        if user.lang_additional:
            for user_lang in user.lang_additional:
                if int(user.language) == int(user_lang.id):
                    remove_language = Language.query.filter_by(id=user_lang.id).first()
                    user.lang_additional.remove(remove_language)
        db.session.commit()
        flash("Info updated","success")
        return redirect(url_for('profile'))
    return render_template("users/edituser.html", form = form, user=user, **languages[lang.code], notifications = notifications)    

@app.route("/addlang_user", methods=['POST','GET'])
def addlang_user():
    """ Physio, new additional language"""
    if not session.get('username'):
        return redirect(url_for('index'))
    if session['user_type'] == 'Patient':
        return redirect(url_for('home'))
    user = User.query.filter_by(id = session['user_id']).first()
    #Get language for user
    lang = Language.query.filter_by(id = session['language']).first()
    notifications = notifications_user()
    #fill form with user data
    form = UpdatinguserForm(obj=user)
    #additional languages for physios
    choices_languages = [(lang_additional.id, lang_additional.title) for lang_additional in Language.query.all()]
    
    #remove primary language from select
    for choices in choices_languages:
        if lang.id == choices[0]:
            choices_languages.remove((choices[0],choices[1]))
            break
    
    #Remove additional languages
    for user_langs in user.lang_additional:    
        for choices in choices_languages:
            if user_langs.id == choices[0]:
                print(user_langs)
                choices_languages.remove((choices[0],choices[1]))
    form.add_language.choices = choices_languages
    if request.method == 'POST':
        new_language = Language.query.filter_by(id=form.add_language.data).first()
        user.lang_additional.append(new_language)
        db.session.commit()
        flash("Info updated","success")
        return redirect(url_for('profile'))
    return render_template('users/addlanguage.html',**languages[lang.code], form=form, notifications = notifications)

@app.route("/rate_us", methods=['POST','GET'])
def rate_us():
    
    if session['user_type'] != 'Patient':
        return redirect(url_for('home'))
    #Get language for user
    lang = Language.query.filter_by(id = session['language']).first()
    user = User.query.filter_by(id = session['user_id']).first()
    notifications = notifications_user()
    rate_byuser_sidebar = True
    if request.method == 'POST':
        rate_value = request.form.get('rating')
        comments = request.form.get('text_rate')       
        if rate_value != None:
            new_rateid = Ratebyusers.query.count()
            new_rateid += 1
            new_rate = Ratebyusers(id = new_rateid , value = rate_value, userid = user.id, comments = comments)
            db.session.add(new_rate)
            db.session.commit()
            flash("Your opinion is really importat for us, thank you!","success")
            redirect(request.url)
        else:
            flash("Please use the stars to rate us.","danger")
    return render_template("rate.html", **languages[lang.code], notifications = notifications, rate_byuser_sidebar=rate_byuser_sidebar)

@app.route("/mytraining")
def mytraining():
    check_trainings()
    if not session.get('username'):
        return redirect(url_for('index'))
    user = User.query.filter_by(id = session['user_id']).first()
    #Get language for user
    lang = Language.query.filter_by(id = session['language']).first()
    notifications = notifications_user()
    #list_exercises = []
    list_training = Training.query.filter_by(patientid = user.id, status = 'In progress').all()
    #for train in list_training:
        #exercise_search = Exercises.query.filter_by(id = train.exercise).first()
        #list_exercises.append(exercise_search)
    list_exercises = Exercises.query.filter_by(category = 1, language = lang.id).order_by(Exercises.id).all()
    return render_template("excercises/mytraining.html", **languages[lang.code], notifications = notifications, 
                            list_exercises = list_exercises, list_training = list_training)   

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/adminedituser/<id>", methods=['POST','GET'])
def adminedit(id):
    """Admin can edit users """
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
    if session['user_type'] == 'Admin':
        user = User.query.filter_by(id = id).first()
        if not user:
            return redirect(url_for('home'))
        language = user.language
        user_type = user.user_type
        status = user.status
        #fill form with user data
        form = AdminUpdateUser(obj=user)
        if request.method == 'POST':
            form.populate_obj(user)
            #if data change, save updated data
            if user.language != language or user.user_type != user_type or user.status != status:
                now = datetime.now() 
                user.updated_at = now.strftime("%Y/%m/%d, %H:%M:%S")
                #If physio, check if has calendarid for googlemeetings, if not add calendar and get calendar id
                if user.user_type == 'Physiotherapist' and user.calendarid == None:
                    idcalendar = createcalendar(user)
                    user.calendarid = idcalendar
                else:
                    pass
                db.session.commit() 
                flash("Info updated","success") 
            else:
                pass
            return redirect(request.url)#redirect(url_for('listusers'))
    else:
        #If not admin redirect
        return redirect(url_for('home'))
    return render_template("admin/edituser.html", form = form, user=user, **languages[lang.code], notifications = notifications)   

@app.route("/createadmin", methods=['POST','GET'])
def createadmin():
    """Create admin user for google calendar, need to use gmail account """
    if session.get('username'):
        return redirect(url_for('home'))
    form = RegisterForm()
    #Validation for email and password
    if form.validate_on_submit():
        user_id     = User.query.count()
        user_id     += 1
        email       = form.email.data
        password    = form.password.data
        first_name  = form.first_name.data
        last_name   = form.last_name.data
        #First time is always for patients 
        user_type   = 'Admin'
        status      = 'Active'
        language    = 1
        # current date and time
        now = datetime.now() 
        DateTime = now.strftime("%Y/%m/%d, %H:%M:%S")
        #Generate token for google calendar and test connection
        #
        if '@gmail.com' in email:
            auth_googlecalendar()
            user = User(id=user_id, first_name=first_name, last_name=last_name, email=email, user_type = user_type, birthdate = DateTime, created_at = DateTime, updated_at = DateTime, status = status, language=language)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            flash("Admin user created!","success")
            #return redirect(url_for('login'))
            redirect(request.url)
        else:
            flash("Please use a gmail account","danger")
    return render_template("users/register.html", form=form)

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

def check_trainings():
    list_training = Training.query.filter_by(status = 'In progress').all()
    now = datetime.now() 
    for train in list_training:
        if train.date_end < now:
            train.status = 'Completed'
    db.session.commit()