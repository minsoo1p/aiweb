import os
import shutil
from dotenv import load_dotenv
import uuid
from werkzeug.utils import secure_filename

from datetime import datetime

from flask import Flask, render_template, redirect, url_for, request, flash, jsonify, send_from_directory, flash
from flask_bootstrap import Bootstrap5
import os
import calendar
from datetime import datetime
from flask_caching import Cache
from urllib.parse import quote_plus, unquote_plus
from bs4 import BeautifulSoup
import requests

from werkzeug.security import generate_password_hash, check_password_hash
# from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.ext.declarative import declarative_base

from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Integer, String, Text, Column, ForeignKey
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, URL
from flask_ckeditor import CKEditor, CKEditorField
from datetime import date, datetime
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from sqlalchemy.orm import relationship

load_dotenv() 

app = Flask(__name__)
app_key = os.getenv('APP_KEY')
hash_method = os.getenv('HASH')
salt = int(os.getenv('SALT'))
app.config['SECRET_KEY'] = app_key
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///posts.db'
app.config['UPLOAD_FOLDER'] = 'static/image'

# Set up SQLAlchemy
db = SQLAlchemy(app)

# Create table in DB
class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    projects = db.relationship('Project', backref='owner', lazy=True)

class Project(db.Model):
    __tablename__ = 'project'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100),nullable=False)
    description = db.Column(db.String(255),nullable=False)
    project_time = db.Column(db.String(100))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    files = db.relationship('File', backref='project', lazy=True)

class File(db.Model):
    __tablename__ = 'file'
    id = db.Column(db.Integer, primary_key=True)
    name1 = db.Column(db.String(100),nullable=False)
    name2 = db.Column(db.String(100),nullable=False)
    image_data = db.Column(db.String(100), nullable=False)
    image_number = db.Column(db.Integer)
    file_time = db.Column(db.String(100))
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return db.session.query(User).get(user_id)

# Initialize database
with app.app_context():
    db.create_all()


@app.route("/")
def main():
    return render_template('index.html')

@app.route("/info")
def info():
    return render_template('information.html')

@app.route("/article")
def article():
    return render_template('article.html')



@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "POST" :
        Email = request.form['email']
        Password = request.form['password']
        user = User.query.filter_by(email=Email).first()
        if user and check_password_hash(user.password, Password) :
            login_user(user)
            return redirect(url_for('project'))
        else : 
            if user : 
                flash('recheck your password')
                return redirect(url_for('login'))
            else : 
                flash('recheck your email')
                return redirect(url_for('login'))

    return render_template("login.html")

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST' :
        Name = request.form['name']
        Email = request.form['email']
        Password = request.form['password']
        hashed_password = generate_password_hash(Password, method=hash_method, salt_length=salt)
        user = User.query.filter_by(email=Email).first() 
        if user :
            flash('You already have ID. Go to Login.')
            return redirect(url_for('register'))
        else :
            new_user = User ( name= Name, email=Email, password=hashed_password)
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('login'))
    return render_template("register.html")

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main'))


@app.route("/project", methods=["GET", "POST"])
@login_required
def project():    
    projects = Project.query.filter_by(user_id=current_user.id).all()
    if request.method == "POST" :
        now = datetime.now()
        current_date = now.strftime("%Y-%m-%d")
        Name = request.form['project-name']
        Des = request.form['project-description']
        new_project = Project(name=Name, description=Des, project_time=current_date, user_id=current_user.id)
        db.session.add(new_project)
        db.session.commit()
        projects = Project.query.filter_by(user_id=current_user.id).all()
        return render_template('project.html', projects = projects)
    return render_template('project.html', projects = projects)

@app.route('/delete_project/<int:project_id>', methods=['GET'])
@login_required
def delete_project(project_id):
    project = Project.query.get(project_id)
    if project:
        db.session.delete(project)
        db.session.commit()
    return redirect(url_for('project'))

location = [
    '',
    'Foot',
    'Ankle',
    'Knee',
    'Hip',
    'Shoulder',
    'Elbow',
    'Wrist',
    'Spine',
    ]
view = [
    '',
    'AnteroPosterior',
    'Lateral',
    'Translateral',
    'Skyline View',
    'Scapula Y View',
    'Whole Lower Extremity (BellThombson)',
    'Whole Spine AnteroPosterior',
    'Whole Spine Lateral',
]

@app.route("/file/<int:project_number>", methods=["GET", "POST"])
@login_required
def file(project_number):
    projects = Project.query.filter_by(user_id=current_user.id).all()
    files = File.query.filter_by(project_id=project_number).all()
    if request.method == "POST":
        now = datetime.now()
        current_date = now.strftime("%Y-%m-%d")
        Name1 = location[int(request.form.get('location'))]
        Name2 = view[int(request.form.get('view'))]
        images = request.files.getlist('files[]')
        image_number = len(images)
        unique_folder_name = str(uuid.uuid4())
        folder_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_folder_name)
        os.makedirs(folder_path, exist_ok=True)
        for image in images:
            image_path = os.path.join(folder_path, image.filename)
            image.save(image_path)
        new_file = File(name1=Name1, name2=Name2, image_data=unique_folder_name, image_number=len(images) ,file_time=current_date, project_id=project_number)
        db.session.add(new_file)
        db.session.commit()
        files = File.query.filter_by(project_id=project_number).all()
        return render_template('file.html', projects=projects, files=files, project_id=project_number, location=location, view=view)
    return render_template('file.html', projects=projects, files=files, project_id=project_number, location=location, view=view)

@app.route('/delete_project/<int:project_number>/<int:file_id>', methods=['GET'])
@login_required
def delete_file(project_number, file_id):
    file = File.query.get(file_id)
    if file:
        folder_path = os.path.join('static', 'image', file.image_data)
        if os.path.exists(folder_path):
            shutil.rmtree(folder_path)
        else :
            os.rmdir(folder_path)
        db.session.delete(file)
        db.session.commit()
    return redirect(url_for('file', project_number=project_number))

# @app.route("/file_location/<int:project_id>/<int:location>", methods=["GET", "POST"])
# @login_required
# def file_location(project_id, location):
#     files = File.query.filter_by(project_id=project_id).all()
#     location = location
#     if request.method == "POST" :
#         now = datetime.now()
#         current_date = now.strftime("%Y-%m-%d")
#         Name1 = location
#         Name2 = request.form.get('view')

#         files = File.query.filter_by(project_id=project_id).all()
#         return redirect('file_location')
#     return render_template('file.html', files=files, location=location)

'''
        Name2 = 
        Img = 
        new_file = File(name1=Name1, name2=Name2, image_data=Img, file_time=current_date, project_id=project_id)
        db.session.add(new_file)
        db.session.commit()
'''

'''
    name1 = db.Column(db.String(100),nullable=False)
    name2 = db.Column(db.String(100),nullable=False)
    image_data = db.Column(db.LargeBinary, nullable=False)
    file_time = db.Column(db.String(100))
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)

'''

@app.route("/processing")
@login_required
def processing():
    return render_template('processing.html')

# @app.route("/angles", methods=['GET', 'POST'])
# def angles():
#     return render_template('angles.html')

if __name__ == '__main__':
    app.run(debug=True)