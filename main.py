import cv2
import numpy as np
from PIL import Image
import base64
from io import BytesIO
import json

import os
import shutil
from dotenv import load_dotenv
import uuid
from werkzeug.utils import secure_filename

from datetime import datetime

from flask import Flask, render_template, redirect, url_for, request, flash, jsonify, send_from_directory, flash
from flask_bootstrap import Bootstrap5
from datetime import datetime

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

from foot_lateral_model import foot_lateral_segmentation

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
    inference_complete = db.Column(db.Boolean, default=False)

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
    
    files = File.query.filter_by(project_id=project_id).all()
    file_ids = []
    for file in files:
        file_ids.append(file.id)
    for file_id in file_ids : 
        file = File.query.get(file_id)
        folder_path = os.path.join('static', 'image', file.image_data)
        if os.path.exists(folder_path):
            shutil.rmtree(folder_path)
        else :
            os.rmdir(folder_path)
        db.session.delete(file)
        db.session.commit()

    project = Project.query.get(project_id)
    if project:
        db.session.delete(project)
        db.session.commit()
    return redirect(url_for('project'))


@app.route("/file/<int:project_number>", methods=["GET", "POST"])
@login_required
def file(project_number):
    projects = Project.query.filter_by(user_id=current_user.id).all()
    files = File.query.filter_by(project_id=project_number).all()
    if request.method == "POST":
        now = datetime.now()
        current_date = now.strftime("%Y-%m-%d")
        Name1 = request.form.get('location')
        Name2 = request.form.get('view')
        images = request.files.getlist('files[]')
        image_number = len(images)
        unique_folder_name = str(uuid.uuid4())
        folder_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_folder_name)
        os.makedirs(os.path.join(folder_path, 'Original'), exist_ok=True)
        os.makedirs(os.path.join(folder_path, 'Segmented'), exist_ok=True)
        os.makedirs(os.path.join(folder_path, 'Lines'), exist_ok=True)
        for image in images:
            image_path = os.path.join(folder_path, 'Original', image.filename)
            image.save(image_path)
        new_file = File(name1=Name1, name2=Name2, image_data=unique_folder_name, image_number=len(images) ,file_time=current_date, project_id=project_number)
        db.session.add(new_file)
        db.session.commit()
        files = File.query.filter_by(project_id=project_number).all()
        return render_template('file.html', projects=projects, files=files, project_id=project_number)
    return render_template('file.html', projects=projects, files=files, project_id=project_number)

@app.route('/delete_file/<int:project_number>/<int:file_id>', methods=['GET'])
@login_required
def delete_file(project_number, file_id):
    file = File.query.get(file_id)
    if file:
        folder_path = os.path.join(app.config['UPLOAD_FOLDER'], file.image_data)
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

# # Example usage
# image_folder = '/content/drive/MyDrive/data/normal'
# images = load_images(image_folder)
# if images is not None:
#     print(f"Loaded {len(images)} images with shape {images.shape}")


def resize_and_pad(image, target_size=(512, 512)):
    h, w = image.shape[:2]
    scale = target_size[0] / max(h, w)
    new_w, new_h = int(w * scale), int(h * scale)
    resized_image = cv2.resize(image, (new_w, new_h))

    delta_w = target_size[1] - new_w
    delta_h = target_size[0] - new_h
    top, bottom = delta_h // 2, delta_h - (delta_h // 2)
    left, right = delta_w // 2, delta_w - (delta_w // 2)

    color = [0, 0, 0]
    new_image = cv2.copyMakeBorder(resized_image, top, bottom, left, right, cv2.BORDER_CONSTANT, value=color)
    
    return new_image

def load_and_process_images(image_folder, target_size=(512, 512)):
    processed_images = []
    image_filenames = sorted(os.listdir(image_folder))

    for image_filename in image_filenames:
        if image_filename.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
            image_path = os.path.join(image_folder, image_filename)
            image = cv2.imread(image_path)
            if image is None:
                print(f"Error reading image: {image_filename}")
                continue

            processed_image = resize_and_pad(image, target_size)
            processed_images.append(processed_image)
    return processed_images

def image_to_base64(image):
    _, buffer = cv2.imencode('.png', image)
    img_str = base64.b64encode(buffer).decode('utf-8')
    return f"data:image/png;base64,{img_str}"

def model_inference(original_image_path, segmented_output_path):
    """
    # AI 모델 돌아가고 segmentation 결과물을 저장하는 함수
    # 
    # image = load_image(original_image_path)
    # segmented_image = run_segmentation_model(image)
    # save_image(segmented_image, segmented_output_path)
    """
    # img = Image.open('HV op 1000.jpg')
    # img.save(segmented_output_path)
    
    pass

def postprocessing_inference(original_image_path, segmented_image_path, line_objects_output_path):
    """
    # segmented output을 이용해 line object를 저장하는 함수
    # 
    # original_image = load_image(original_image_path)
    # segmented_image = load_image(segmented_image_path)
    # line_objects = generate_line_objects(original_image, segmented_image)
    # save_json(line_objects, line_objects_output_path)
    """
    # with open('tmp/line_objects.json', 'r') as file:
    #     data = json.load(file)
    
    # with open(line_objects_output_path, 'w') as file:
    #     json.dump(data, file, indent=4)
    
    pass

@app.route("/processing/<int:project_id>/<int:file_id>", methods=['GET','POST'])
@login_required
def processing(project_id, file_id):
    file = File.query.get(file_id)
    projects = Project.query.filter_by(user_id=current_user.id).all()

    folder_path = os.path.join(app.config['UPLOAD_FOLDER'], file.image_data)

    original_images = [url_for('static', filename=f'image/{file.image_data}/Original/{img}') 
                        for img in sorted(os.listdir(os.path.join(folder_path, 'Original'))) 
                        if img.lower().endswith(('.png', '.jpg', '.jpeg'))]
    segmented_images = [url_for('static', filename=f'image/{file.image_data}/Segmented/{img}') 
                        for img in sorted(os.listdir(os.path.join(folder_path, 'Segmented'))) 
                        if img.lower().endswith(('.png', '.jpg', '.jpeg'))]
    
    # processed_original_images = load_and_process_images(original_images)
    # processed_segmented_images = load_and_process_images(segmented_images)
    
    # visualized_original_images = [image_to_base64(img) for img in processed_original_images]
    # visualized_segmented_images = [image_to_base64(img) for img in processed_segmented_images]

    line_objects = []
    for json_file in sorted(os.listdir(os.path.join(folder_path, 'Lines'))):
        if json_file.lower().endswith('.json'):
            with open(os.path.join(folder_path, 'Lines', json_file), 'r') as f:
                line_objects.append(json.load(f))

    return render_template('processing.html', projects=projects, file=file, images=original_images,
                           segmented_images=segmented_images, line_objects=line_objects)


# @app.route("/angles", methods=['GET', 'POST'])
# def angles():
#     return render_template('angles.html')

@app.route("/batch_inference/<int:project_id>/<int:file_id>")
@login_required
def batch_inference(project_id, file_id):
    file = File.query.get(file_id)
    
    if file and file.project_id == project_id:
        image_folder = os.path.join(app.config['UPLOAD_FOLDER'], file.image_data)
        
        original_folder = os.path.join(image_folder, 'Original')
        segmented_folder = os.path.join(image_folder, 'Segmented')
        lines_folder = os.path.join(image_folder, 'Lines')

        os.makedirs(segmented_folder, exist_ok=True)
        os.makedirs(lines_folder, exist_ok=True)
        
        for image_file in os.listdir(original_folder):
            if image_file.lower().endswith(('.png', '.jpg', '.jpeg', '.PNG', '.JPG', '.JPEG')):
                root, ext = os.path.splitext(image_file)
                
                original_path = os.path.join(original_folder, image_file)
                segmented_path = os.path.join(segmented_folder, f"{root}_segmented.jpg")
                line_objects_path = os.path.join(lines_folder, f"{root}_lines.json")
                
                model_inference(original_path, segmented_path)
                postprocessing_inference(original_path, segmented_path, line_objects_path)
        
        file.inference_complete = True
        db.session.commit()
        
        flash('Batch inference completed successfully for the selected file.')
    else:
        flash('Invalid file or permission denied.')
    
    return redirect(url_for('file', project_number=project_id))

@app.route("/inference/<int:image_id>")
@login_required
def single_inference(image_id):
    file = File.query.get(image_id)
    
    if file and file.user_id == current_user.id:
        image_folder = os.path.join('static', 'image', file.image_data)
        original_folder = os.path.join(image_folder, 'original')
        segmented_folder = os.path.join(image_folder, 'segmented')
        lines_folder = os.path.join(image_folder, 'lines')
        
        # 필요한 폴더 생성
        os.makedirs(segmented_folder, exist_ok=True)
        os.makedirs(lines_folder, exist_ok=True)
        
        for image_file in os.listdir(original_folder):
            if image_file.lower().endswith(('.png', '.jpg', '.jpeg')):
                original_path = os.path.join(original_folder, image_file)
                segmented_path = os.path.join(segmented_folder, f"segmented_{image_file}")
                line_objects_path = os.path.join(lines_folder, f"{os.path.splitext(image_file)[0]}_lines.json")
                
                model_inference(original_path, segmented_path)
                postprocessing_inference(original_path, segmented_path, line_objects_path)
        
        flash('Inference completed successfully for the selected image.')
    else:
        flash('Invalid image or permission denied.')
    
    return redirect(url_for('project'))


if __name__ == '__main__':
    app.run(debug=True)