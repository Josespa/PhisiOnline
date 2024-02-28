import os.path
from src import app, db, ALLOWED_EXTENSIONS
from .models import User, Language
from .forms import LoginForm, RegisterForm, UpdatinguserForm,UploadphotoForm, AdminUpdateUser
from flask import render_template, request, jsonify, Response, redirect, flash, url_for, session
from datetime import datetime
from werkzeug.utils import secure_filename
from src.googlecalendar.googlecalendar import createcalendar
from src.languages.languages import languages

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
        user = User(id=user_id, first_name=first_name, last_name=last_name, email=email, user_type = user_type, birthday = DateTime, created_at = DateTime, updated_at = DateTime, status = status, language=language)
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
    return render_template("users/profile.html", user=user, language = lang, **languages[lang.code])

@app.route("/updateprofile", methods=['POST','GET'])
def edituser():
    if not session.get('username'):
        return redirect(url_for('index'))
    user = User.query.filter_by(id = session['user_id']).first()
    #Get language for user
    lang = Language.query.filter_by(id = session['language']).first()
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
        db.session.commit()
        return redirect(url_for('profile'))
    return render_template("users/edituser.html", form = form, user=user, **languages[lang.code])    

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/adminedituser/<id>", methods=['POST','GET'])
def adminedit(id):
    if not session.get('username'):
        return redirect(url_for('index'))
    user = User.query.filter_by(id = session['user_id']).first()
    #Get language for user
    lang = Language.query.filter_by(id = session['language']).first()
    if session['user_type'] == 'Admin':
        user = User.query.filter_by(id = id).first()
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
            else:
                pass
            return redirect(url_for('listusers'))
    else:
        #If not admin redirect
        return redirect(url_for('home'))
    return render_template("admin/edituser.html", form = form, user=user, **languages[lang.code])   

