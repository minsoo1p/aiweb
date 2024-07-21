import os
from dotenv import load_dotenv

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

# Set up SQLAlchemy
db = SQLAlchemy(app)

# Create table in DB
class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))


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
            return render_template('project.html')
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


@app.route("/project")
@login_required
def project():
    return render_template('project.html')

@app.route("/file")
@login_required
def file():
    return render_template('file.html')

@app.route("/processing")
@login_required
def processing():
    return render_template('processing.html')

# @app.route("/angles", methods=['GET', 'POST'])
# def angles():
#     return render_template('angles.html')

if __name__ == '__main__':
    app.run(debug=True)