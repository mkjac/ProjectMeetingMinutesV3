from flask_login import LoginManager, login_user, current_user, logout_user, login_required
from flask import flash, render_template, redirect, url_for, request
from datetime import datetime as dt
import os
from werkzeug.utils import secure_filename
import shutil
import psycopg2

from Application.models import *
from Application.forms import *

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    return User.query.filter_by(id=user_id).first()


@app.route('/', methods=['POST', 'GET'])
@app.route('/login', methods=['POST', 'GET'])
def login():
    login_form = LoginForm()

    if login_form.validate_on_submit():
        username_entered = login_form.username.data
        password_entered = login_form.password.data

        user_object = User.query.filter_by(username=username_entered).first()
        if user_object is None:
            flash("Username doesn't exist")
        elif password_entered != user_object.password:
            flash("Password is incorrect")
        else:
            login_user(user_object)
            return redirect(url_for('home'))

    return render_template("login.html", form=login_form)


@app.route('/register', methods=['POST', 'GET'])
def register():
    reg_form = RegistrationForm()
    if reg_form.validate_on_submit():
        username = reg_form.username.data
        password = reg_form.password.data

        userObject = User.query.filter_by(username=username).first()
        if userObject:
            flash("Username taken")
            return render_template("register.html", form=reg_form)

        user = User(username=username, password=password)
        db.session.add(user)
        db.session.commit()
        flash("Registered")
        return redirect(url_for('login'))
    return render_template("register.html", form=reg_form)


@app.route('/home', methods=['POST', 'GET'])
@login_required
def home():
    if current_user:
        currentUser = current_user
    else:
        currentUser = None

    minutesList = Minute.query.filter_by(userid=currentUser.id)
    actionsList = Action.query.all()
    filesList = Files.query.all()

    return render_template("home.html", currentUser=currentUser, minutesList=minutesList, actionsList=actionsList, filesList=filesList)


@app.route('/new', methods=['POST', 'GET'])
@login_required
def new():
    new_form = NewForm()
    actions_form = ActionsForm()
    if new_form.validate_on_submit():
        minute = Minute(userid=current_user.id, datetime=dt.combine(
            new_form.date.data, new_form.time.data),
            attendees=new_form.attendees.data, absentees=new_form.absentees.data, agenda=new_form.agenda.data, extrainfo=new_form.extraInfo.data)
        db.session.add(minute)
        db.session.commit()

        actionsData = request.form.getlist('action')
        actionedByData = request.form.getlist('actionedBy')

        meetingid = Minute.query.order_by(
            Minute.meetingid.desc()).first().meetingid

        for i in range(len(actionsData)):
            action = Action(meetingid=meetingid,
                            action=actionsData[i], actionedby=actionedByData[i])
            db.session.add(action)
        if new_form.files.data:
            fileData = new_form.files.data
            fileData.save(os.path.join(os.path.abspath(os.path.dirname(
                __file__)), app.config['UPLOAD_FOLDER'], secure_filename(fileData.filename)))

            file = Files(meetingid=meetingid,
                         filename=new_form.files.data.filename)
            db.session.add(file)

        db.session.commit()

        flash("Minute added")
        return redirect(url_for('home'))

    return render_template("new.html", newForm=new_form, actionsForm=actions_form)


@app.route('/downloadfile/<int:fileid>', methods=['POST', 'GET'])
def downloadfile(fileid):
    file_record = Files.query.filter_by(fileid=fileid).first()

    if os.name == "nt":
        DOWNLOAD_FOLDER = f"" + \
            os.getenv('USERPROFILE') + "\\Downloads\\" + \
            secure_filename(file_record.filename)
    else:
        DOWNLOAD_FOLDER = r"{os.getenv('HOME')}/Downloads"

    shutil.copyfile(os.path.join(os.path.abspath(os.path.dirname(
        __file__)), app.config['UPLOAD_FOLDER'], secure_filename(file_record.filename)), DOWNLOAD_FOLDER)
    flash('File downloaded into downloads folder')

    return redirect(url_for('home'))


@app.route('/delete/<int:meetingid>', methods=['POST', 'GET'])
def delete(meetingid):
    record = Minute.query.filter_by(meetingid=meetingid).first()
    actionRecords = Action.query.filter_by(meetingid=meetingid).all()
    fileRecords = Files.query.filter_by(meetingid=meetingid).all()
    for f in fileRecords:
        db.session.delete(f)
    for act in actionRecords:
        db.session.delete(act)
    db.session.delete(record)
    db.session.commit()
    return redirect(url_for('home'))


@app.route('/modify/<int:meetingid>', methods=['POST', 'GET'])
def modify(meetingid):
    new_form = NewForm()
    actions_form = ActionsForm()

    record = Minute.query.filter_by(meetingid=meetingid).first()
    actionRecords = Action.query.filter_by(meetingid=meetingid).all()
    fileRecords = Files.query.filter_by(meetingid=meetingid).all()

    new_form.agenda.data = record.agenda
    new_form.attendees.data = record.attendees
    new_form.absentees.data = record.absentees
    new_form.extraInfo.data = record.extrainfo
    new_form.date.data = dt.date(record.datetime)
    new_form.time.data = dt.time(record.datetime)

    for f in fileRecords:
        db.session.delete(f)
    for act in actionRecords:
        db.session.delete(act)
    db.session.delete(record)

    db.session.commit()
    if new_form.validate_on_submit():
        minute = Minute(userid=current_user.id, datetime=dt.combine(
            new_form.date.data, new_form.time.data),
            attendees=new_form.attendees.data, absentees=new_form.absentees.data, agenda=new_form.agenda.data, extrainfo=new_form.extraInfo.data)
        db.session.add(minute)
        db.session.commit()

        actionsData = request.form.getlist('action')
        actionedByData = request.form.getlist('actionedBy')

        meetingid = Minute.query.order_by(
            Minute.meetingid.desc()).first().meetingid

        for i in range(len(actionsData)):
            action = Action(meetingid=meetingid,
                            action=actionsData[i], actionedby=actionedByData[i])
        db.session.add(action)
        if new_form.files.data:
            fileData = new_form.files.data
            fileData.save(os.path.join(os.path.abspath(os.path.dirname(
                __file__)), app.config['UPLOAD_FOLDER'], secure_filename(fileData.filename)))

            file = Files(meetingid=meetingid,
                         filename=new_form.files.data.filename)
            db.session.add(file)

        db.session.commit()

        return redirect(url_for('home'))
    return render_template('new.html', newForm=new_form, actionsForm=actions_form)


@app.route('/logout', methods=['POST', 'GET'])
@login_required
def logout():
    logout_user()
    flash("Succesfully logged out")
    return redirect(url_for('login'))


if __name__ == "__main__":
    app.run(host='localhost', port=81, debug=True)
