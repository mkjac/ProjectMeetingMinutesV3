from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

app = Flask(__name__, template_folder='templates', static_folder='static')
app.secret_key = 'secret'

# Fetch password
file = open("password.txt")
passwordString = file.read()
file.close()

# Configure Database
connString = 'postgresql+psycopg2://postgres:' + \
    passwordString + '@localhost:5432/MeetingMinutes'

app.config['SQLALCHEMY_DATABASE_URI'] = connString
app.config['UPLOAD_FOLDER'] = 'application\\static\\files'
db = SQLAlchemy(app)


class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(), nullable=False)

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)


class Minute(db.Model):
    """ Minutes Model """
    __tablename__ = 'minutes'
    __table_args__ = {'quote': False, 'extend_existing': True}
    userid = db.Column(db.Integer, db.ForeignKey("users.id"))
    meetingid = db.Column(db.Integer, primary_key=True)
    datetime = db.Column(db.DateTime, nullable=False)
    attendees = db.Column(db.String(1000), nullable=False)
    absentees = db.Column(db.String(1000))
    agenda = db.Column(db.String(1000), nullable=False)
    extrainfo = db.Column(db.String(1000))


class Action(db.Model):
    """ Actions Model """
    __tablename__ = "actions"
    actionid = db.Column(db.Integer, primary_key=True)
    meetingid = db.Column(db.Integer, db.ForeignKey('minutes.meetingid'))
    action = db.Column(db.String(500), nullable=False)
    actionedby = db.Column(db.String(500), nullable=False)


class Files(db.Model):
    """ Files Model """
    __tablename__ = "files"
    fileid = db.Column(db.Integer, primary_key=True)
    meetingid = db.Column(db.Integer, db.ForeignKey('minutes.meetingid'))
    filename = db.Column(db.String(100), nullable=False)
