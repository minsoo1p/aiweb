import tensorflow as tf

import cv2
from cv2 import ximgproc
import numpy as np
from PIL import Image, ImageOps
import base64
from io import BytesIO
import json
import csv
import ast

import re
import os
import json
import shutil
from dotenv import load_dotenv
import uuid
from werkzeug.utils import secure_filename

from flask import Flask, render_template, redirect, url_for, request, flash, jsonify, send_from_directory, flash, send_file
from flask_bootstrap import Bootstrap5
from threading import Thread

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
from image_processing import Process
from post_processing import Cleaning_contour, Post_processing
from kind_detection import Preprocessing

load_dotenv() 

app = Flask(__name__)
app_key = os.getenv('APP_KEY')
hash_method = os.getenv('HASH')
salt = int(os.getenv('SALT'))
# socketio = SocketIO(app, async_mode='gevent')
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
    selected_angles = db.Column(db.Text,nullable=False)
    image_data = db.Column(db.String(100), nullable=False)
    image_number = db.Column(db.Integer)
    file_time = db.Column(db.String(100))
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    status = db.Column(db.String, default='pending')
    progress = db.Column(db.Float, default=0)
    
# class DataTable(db.Model):
#     __tablename__ = 'data_table'
#     id = db.Column(db.Integer, primary_key=True)
#     file_id = db.Column(db.Integer, db.ForeignKey('file.id'), nullable=False)
#     image_name = db.Column(db.String(100), nullable=False)
#     HVA = db.Column(db.Float)
#     DMAA = db.Column(db.Float)
#     IMA = db.Column(db.Float)
#     talocalcaneal = db.Column(db.Float)
#     talonavicular = db.Column(db.Float)
#     incongruency = db.Column(db.Float)
#     tibiocalcaneal = db.Column(db.Float)
#     calcanealpitch = db.Column(db.Float)
#     meary = db.Column(db.Float)
#     # gissane = db.Column(db.Float)
#     # bohler = db.Column(db.Float)

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

def cv2_imread(file):
    in_memory_file = BytesIO()
    file.save(in_memory_file)
    in_memory_file.seek(0)
    
    np_img = np.frombuffer(in_memory_file.read(), np.uint8)

    img = cv2.imdecode(np_img, cv2.IMREAD_COLOR)

    return img



# 사진을 올리는 순간 processed 파일 생성 
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
        
        checkbox_angles = request.form.getlist('angles')
        Selected_angles = json.dumps(checkbox_angles)
        
        unique_folder_name = str(uuid.uuid4())
        folder_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_folder_name)
        os.makedirs(os.path.join(folder_path, 'Processed'), exist_ok=True)
        for image in images:
            image_path = os.path.join(folder_path, image.filename)
            image.save(image_path)

        new_file = File(name1=Name1, name2=Name2, selected_angles=Selected_angles, image_data=unique_folder_name, image_number=len(images) ,file_time=current_date, project_id=project_number)
        db.session.add(new_file)
        db.session.commit()
        files = File.query.filter_by(project_id=project_number).all()
        
        for file in files:
            file.selected_angles = ast.literal_eval(file.selected_angles)

        return redirect(url_for('file', project_number=project_number))
    
    for file in files:
        file.selected_angles = ast.literal_eval(file.selected_angles)
    return render_template('file.html', projects=projects, files=files, project_id=project_number)

# selected_angles를 jinja template 내에서 list로 변환하기 위해 사용
@app.template_filter('parse_json')
def parse_json(value):
    try:
        return json.loads(value)
    except:
        return []

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


@app.route("/processing/<int:project_id>/<int:file_id>", methods=['GET','POST'])
@login_required
def processing(project_id, file_id):
    file = File.query.get(file_id)
    projects = Project.query.filter_by(user_id=current_user.id).all()

    folder_path = os.path.join(app.config['UPLOAD_FOLDER'], file.image_data)
    processed_folder = os.path.join(folder_path, 'Processed')

    # original_images = [url_for('static', filename=f'image/{file.image_data}/{img}') 
    #                     for img in sorted(os.listdir(folder_path)) 
    #                     if img.lower().endswith(('.png', '.jpg', '.jpeg'))]

    preprocessed_images = {}
    number = 1
    for img in sorted(os.listdir(processed_folder)):
        if img.lower().endswith(('original.png', 'original.jpg', 'original.jpeg')):
            index = img.split('_')[0]
            if '-' in index : 
                primary_index = index.split('-')[0]
                secondary_index = index.split('-')[1]
                preprocessed_images[number] = url_for('static', filename=f'image/{file.image_data}/Processed/{img}')
                number += 1
            else : 
                preprocessed_images[number] = url_for('static', filename=f'image/{file.image_data}/Processed/{img}')
                number += 1 

    # preprocessed_images = [url_for('static', filename=f'image/{file.image_data}/Processed/{img}') 
    #                     for img in sorted(os.listdir(os.path.join(folder_path, 'Processed')), key=lambda file: int(file.split('_')[0])) 
    #                     if img.lower().endswith(('original.png', 'original.jpg', 'original.jpeg'))]

    
    # processed_original_images = load_and_process_images(original_images)
    # processed_segmented_images = load_and_process_images(segmented_images)
    
    # visualized_original_images = [image_to_base64(img) for img in processed_original_images]
    # visualized_segmented_images = [image_to_base64(img) for img in processed_segmented_images]

    
    # for img_folder in sorted(os.listdir(folder_path)):
    #     img_path = os.path.join(folder_path, img_folder)
    #     if os.path.isdir(img_path):
    #         segmented_images[img_folder] = [
    #             url_for('static', filename=f'image/{file.image_data}/{img}')
    #             for img in sorted(os.listdir(img_path))
    #             if img.lower().endswith(('.png', '.jpg', '.jpeg'))
    #         ]
    segmented_images = {}
    number = 0
    guide = ''
    for img in sorted(os.listdir(processed_folder)):
        if img.lower().endswith(('.png', '.jpg', '.jpeg')) and not img.lower().endswith(('_original.png', '_original.jpg', '_original.jpeg')):
            root, ext = os.path.splitext(img)
            parts = root.split('_')
            if len(parts) > 2:
                if guide == parts[0] :
                    if '-' in parts[0]:
                        original_name = '_'.join(parts[1:-1])
                        seg_type = parts[-1]
                        if number not in segmented_images:
                            segmented_images[number] = {}
                            segmented_images[number]['name'] = original_name
                        segmented_images[number][seg_type] = url_for('static', filename=f'image/{file.image_data}/Processed/{img}')
                    else :
                        original_name = '_'.join(parts[1:-1])
                        seg_type = parts[-1]
                        if number not in segmented_images:
                            segmented_images[number] = {}
                            segmented_images[number]['name'] = original_name
                        segmented_images[number][seg_type] = url_for('static', filename=f'image/{file.image_data}/Processed/{img}')
                elif guide != parts[0] : 
                    number += 1
                    guide = parts[0]
                    if '-' in parts[0]:
                        original_name = '_'.join(parts[1:-1])
                        seg_type = parts[-1]
                        if number not in segmented_images:
                            segmented_images[number] = {}
                            segmented_images[number]['name'] = original_name
                        segmented_images[number][seg_type] = url_for('static', filename=f'image/{file.image_data}/Processed/{img}')
                            
                    else :
                        if len(parts) > 2:
                            original_name = '_'.join(parts[1:-1])
                            seg_type = parts[-1]
                            if number not in segmented_images:
                                segmented_images[number] = {}
                                segmented_images[number]['name'] = original_name
                            segmented_images[number][seg_type] = url_for('static', filename=f'image/{file.image_data}/Processed/{img}')

    number = 1
    line_objects = {}
    for lines in sorted(os.listdir(processed_folder)):
        if lines.lower().endswith('.json'):
            root, ext = os.path.splitext(lines)
            parts = root.split('_')
            if '-' in parts[0] :
                primary_index = parts[0].split('-')[0]
                secondary_index = parts[0].split('-')[1]
                original_name = '_'.join(parts[1:-1])
                with open(os.path.join(processed_folder, lines), 'r') as f:
                    try:
                        line_objects[number] = {
                            'name': original_name,
                            'content': json.load(f)
                        }
                    except json.JSONDecodeError:
                        print(f"Error decoding JSON file: {lines}")
                        line_objects[root] = {}
                number += 1
            else : 
                index = int(parts[0])
                original_name = '_'.join(parts[1:-1])
                with open(os.path.join(processed_folder, lines), 'r') as f:
                    try:
                        line_objects[number] = {
                            'name': original_name,
                            'content': json.load(f)
                        }
                    except json.JSONDecodeError:
                        print(f"Error decoding JSON file: {lines}")
                        line_objects[root] = {}
                number += 1
                    
    # Read angle data from CSV
    csv_file_path = os.path.join(processed_folder, 'angles.csv')
    angle_data = []
    if os.path.exists(csv_file_path):
        with open(csv_file_path, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            angle_data = list(reader)
            
    file.selected_angles = ast.literal_eval(file.selected_angles)

    return render_template('processing.html', 
                           projects=projects, 
                           file=file, 
                           original_images=preprocessed_images,
                           segmented_images=segmented_images, 
                           line_objects=json.dumps(line_objects),
                           angle_data=angle_data)

# Processing page에서 'save and export data' 버튼 누르면 변경된 데이터를 저장
@app.route('/save_and_download/<int:file_id>', methods=['POST'])
@login_required
def save_and_download(file_id):
    file = File.query.get(file_id)
    selectedAngles = ast.literal_eval(file.selected_angles)
    
    if not file:
        return jsonify({'error': 'File not found'}), 404

    data = request.json
    csv_file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.image_data, 'Processed', 'angles.csv')
    print(data)

    # Update CSV file
    with open(csv_file_path, 'w', newline='') as csvfile:
        fieldnames = ['image_name'] + selectedAngles
        fieldnames = [item.replace("'", "").replace(" ", "_") for item in fieldnames]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in data:
            writer.writerow(row)

    # Send file for download
    return send_file(csv_file_path, as_attachment=True, attachment_filename='angles.csv')

class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        return super(NumpyEncoder, self).default(obj)


def size_regurizer(image):
    # image = cv2.imread(image_path)
    height, width = image.shape[:2]
    
    if height > width:
        padding = (height - width) // 2
        square_image = cv2.copyMakeBorder(image, 0, 0, padding, padding, cv2.BORDER_CONSTANT, value=[0, 0, 0])
    elif width > height:
        padding = (width - height) // 2
        square_image = cv2.copyMakeBorder(image, padding, padding, 0, 0, cv2.BORDER_CONSTANT, value=[0, 0, 0])
    else:
        square_image = image  # cropped_image를 사용하지 않았으므로 image로 대체

    resized_image = cv2.resize(square_image, (512, 512))
    return resized_image

# @socketio.on('connect')
# def test_connect():
#     if not current_user.is_authenticated:
#         return False  
#     else:
#         emit('my response', {'data': 'Connected'})
#         return True 


# @socketio.on('start_inference')
# def batch_inference(data):
#     project_id = data['project_id']
#     file_id = data['file_id']
#     file = File.query.get(file_id)
#     selectedAngles = ast.literal_eval(file.selected_angles)
    
#     angle_to_seglist = {
#         'TibioCalcaneal Angle': ['tib', 'cal'],
#         'TaloCalcaneal Angle': ['tal', 'cal'],
#         'Calcaneal Pitch': ['cal', 'm5'],
#         "Meary's Angle": ['tal', 'm1']
#     }
    
#     seglist = []
#     for selectedAngle in selectedAngles:
#         seglist += angle_to_seglist[selectedAngle]
#     segset = set(seglist)
    
#     if file and file.project_id == project_id:
#         try:
#             image_folder = os.path.join(app.config['UPLOAD_FOLDER'], file.image_data)
#             seglist = list(segset)
#             seg = foot_lateral_segmentation('static/models/kind_detection_yolov8_model.pt',*seglist)
#             #total processing count
#             image_number = len([f for f in os.listdir(image_folder) if f.endswith(('.png', '.jpg', '.jpeg', '.PNG', '.JPG', '.JPEG'))])
#             count = 0
#             file.status = 'processing'
#             db.session.commit()
            
            
#             #CSV creation
#             fieldnames = ['image_name'] + selectedAngles
#             fieldnames = [item.replace("'", "").replace(" ", "_") for item in fieldnames]
#             csv_file_path = os.path.join(image_folder, 'Processed', f'angles.csv')
#             with open(csv_file_path, 'w', newline='') as csvfile:
#                 writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
#                 writer.writeheader()
                
#                 for index, image_file in enumerate(sorted([f for f in os.listdir(image_folder) if f.endswith(('.png', '.jpg', '.jpeg', '.PNG', '.JPG', '.JPEG'))])):
#                     full_image_path = os.path.join(image_folder, image_file)
#                     image = Image.open(full_image_path)
#                     root, ext = os.path.splitext(image_file)
                    
                    
#                     # image = seg.preprocess(full_image_path)
#                     # resized_image = size_regurizer(full_image_path)
#                     original_image = cv2.imread(full_image_path)
#                     results = seg.detect_and_crop(original_image)
#                     # process = Preprocessing(resized_image)
#                     # results = process.cropping()

#                     num_boxes = len(results)

#                     if num_boxes == 1 :
#                         image = results[0]['image']
#                         box = results[0]['box']
#                         type = results[0]['type']

#                         _, masks = seg.segmentation(image)

#                         resized_original_image = size_regurizer(original_image)
#                         seg.to_JPG(resized_original_image, os.path.join(image_folder, 'Processed', f'{index+1}_{root}_original{ext}'))
                        
#                         masks = {key: seg.returned(original_image, image, box) for key, image in masks.items()}
#                         masks = {key: size_regurizer(image) for key, image in masks.items()}

#                         clean_mask = Cleaning_contour()
#                         cleaned_masks = {}
#                         for input in masks :
#                             clean_contour = clean_mask.clean_contour(masks[input])
#                             arc_contour = clean_mask.arc_contour(clean_contour)
#                             decay_contour = clean_mask.decay_contour(arc_contour) 
#                             cleaned_masks[input] = decay_contour

#                             output_path = os.path.join(image_folder, 'Processed', f'{index+1}_{root}_{input}{ext}')
#                             seg.to_JPG(cleaned_masks[input],output_path)
                        

#                         post_data = Post_processing(cleaned_masks)
#                         data = post_data.postProcess()
#                         count += 1
#                         socketio.emit('inference_progress', {'file_id': file_id, 'progress': round(count/image_number * 100, 1)})

#                         file_path = os.path.join(image_folder, 'Processed', f'{index+1}_{root}_postline.json')
#                         with open(file_path, 'w') as json_file:
#                             json.dump(data, json_file, cls=NumpyEncoder, indent=4)
                            
#                         writer.writerow({key:root if key=='image_name' else 'n/a' for key in fieldnames})

#                     elif num_boxes >= 2:
#                         image_number += (num_boxes - 1)
#                         number = 1
#                         resized_original_image = size_regurizer(original_image)
#                         for result in results : 
#                             image = result['image']
#                             box = result['box']
#                             result_type = result['type']

#                             _, masks = seg.segmentation(image)

#                             seg.to_JPG(resized_original_image, os.path.join(image_folder, 'Processed', f'{index+1}-{number}_{root}_original{ext}'))
                            
#                             masks = {key: seg.returned(original_image, image, box) for key, image in masks.items()}
#                             masks = {key: size_regurizer(image) for key, image in masks.items()}

#                             clean_mask = Cleaning_contour()
#                             cleaned_masks = {}
#                             for input in masks :
#                                 clean_contour = clean_mask.clean_contour(masks[input])
#                                 arc_contour = clean_mask.arc_contour(clean_contour)
#                                 decay_contour = clean_mask.decay_contour(arc_contour) 
#                                 cleaned_masks[input] = decay_contour

#                                 output_path = os.path.join(image_folder, 'Processed', f'{index+1}-{number}_{root}_{input}{ext}')
#                                 seg.to_JPG(cleaned_masks[input],output_path)
                            

#                             post_data = Post_processing(cleaned_masks)
#                             data = post_data.postProcess()


#                             file_path = os.path.join(image_folder, 'Processed', f'{index+1}-{number}_{root}_postline.json')
#                             with open(file_path, 'w') as json_file:
#                                 json.dump(data, json_file, cls=NumpyEncoder, indent=4)
                                
#                             writer.writerow({key:f'{root}_{number}'if key==f'image_name' else 'n/a' for key in fieldnames})
#                             number += 1
#                             count += 1
#                             socketio.emit('inference_progress', {'file_id': file_id, 'progress': round(count/image_number * 100, 1)})



#             file.status = 'completed'
#             db.session.commit()
#             socketio.emit('inference_complete', {'file_id': file_id, 'status': 'completed'})
            
#             print('Batch inference completed successfully for the selected file.')
            
#         except Exception as e:
#             print(f"Error processing image: {e}")
#             file.status = 'failed'
#             db.session.commit()
#             emit('inference_complete', {'file_id': file_id, 'status': 'failed'})
#     else:
#         print('Invalid file or permission denied.')
    
#     return redirect(url_for('file', project_number=project_id))

@app.route('/batch_inference/<int:project_id>/<int:file_id>', methods=['POST', 'GET'])
def batch_inference(project_id, file_id):
    file = File.query.get(file_id)
    if not file or file.project_id != project_id:
        return jsonify({"error": "File not found or permission denied"}), 404
    
    if request.method == 'POST':
        if file.status == 'pending':
            file.status = 'processing'
            file.progress = 0
            db.session.commit()
            Thread(target=run_inference, args=(project_id, file_id)).start()
        return jsonify({
            'status': 'processing',
            'progress': file.progress
        }), 202
        
    elif request.method == 'GET':
        return jsonify({
            'status': file.status,
            'progress': file.progress
        })
        
def run_inference(project_id, file_id):
    file = File.query.get(file_id)
    if not file or file.project_id != project_id:
        return jsonify({"error": "File not found or permission denied"}), 404
    
    try:
        selectedAngles = ast.literal_eval(file.selected_angles)
        
        angle_to_seglist = {
            'TibioCalcaneal Angle': ['tib', 'cal'],
            'TaloCalcaneal Angle': ['tal', 'cal'],
            'Calcaneal Pitch': ['cal', 'm5'],
            "Meary's Angle": ['tal', 'm1']
        }
        
        seglist = []
        for selectedAngle in selectedAngles:
            seglist += angle_to_seglist[selectedAngle]
        segset = set(seglist)
        
        image_folder = os.path.join(app.config['UPLOAD_FOLDER'], file.image_data)
        seglist = list(segset)
        seg = foot_lateral_segmentation('static/models/kind_detection_yolov8_model.pt',*seglist)
        #total processing count
        image_number = len([f for f in os.listdir(image_folder) if f.endswith(('.png', '.jpg', '.jpeg', '.PNG', '.JPG', '.JPEG'))])
        count = 0
        file.status = 'processing'
        db.session.commit()
        
        
        #CSV creation
        fieldnames = ['image_name'] + selectedAngles
        fieldnames = [item.replace("'", "").replace(" ", "_") for item in fieldnames]
        csv_file_path = os.path.join(image_folder, 'Processed', f'angles.csv')
        with open(csv_file_path, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for index, image_file in enumerate(sorted([f for f in os.listdir(image_folder) if f.endswith(('.png', '.jpg', '.jpeg', '.PNG', '.JPG', '.JPEG'))])):
                full_image_path = os.path.join(image_folder, image_file)
                image = Image.open(full_image_path)
                root, ext = os.path.splitext(image_file)
                
                
                # image = seg.preprocess(full_image_path)
                # resized_image = size_regurizer(full_image_path)
                original_image = cv2.imread(full_image_path)
                results = seg.detect_and_crop(original_image)
                # process = Preprocessing(resized_image)
                # results = process.cropping()

                num_boxes = len(results)

                if num_boxes == 1 :
                    image = results[0]['image']
                    box = results[0]['box']
                    type = results[0]['type']

                    _, masks = seg.segmentation(image)

                    resized_original_image = size_regurizer(original_image)
                    seg.to_JPG(resized_original_image, os.path.join(image_folder, 'Processed', f'{index+1}_{root}_original{ext}'))
                    
                    masks = {key: seg.returned(original_image, image, box) for key, image in masks.items()}
                    masks = {key: size_regurizer(image) for key, image in masks.items()}

                    clean_mask = Cleaning_contour()
                    cleaned_masks = {}
                    for input in masks :
                        clean_contour = clean_mask.clean_contour(masks[input])
                        arc_contour = clean_mask.arc_contour(clean_contour)
                        decay_contour = clean_mask.decay_contour(arc_contour) 
                        cleaned_masks[input] = decay_contour

                        output_path = os.path.join(image_folder, 'Processed', f'{index+1}_{root}_{input}{ext}')
                        seg.to_JPG(cleaned_masks[input],output_path)
                    

                    post_data = Post_processing(cleaned_masks)
                    data = post_data.postProcess()

                    file_path = os.path.join(image_folder, 'Processed', f'{index+1}_{root}_postline.json')
                    with open(file_path, 'w') as json_file:
                        json.dump(data, json_file, cls=NumpyEncoder, indent=4)
                        
                    writer.writerow({key:root if key=='image_name' else 'n/a' for key in fieldnames})
                    
                    count += 1
                    file.progress = (count / image_number) * 100
                    db.session.commit()

                elif num_boxes >= 2:
                    image_number += (num_boxes - 1)
                    number = 1
                    resized_original_image = size_regurizer(original_image)
                    for result in results : 
                        image = result['image']
                        box = result['box']
                        result_type = result['type']

                        _, masks = seg.segmentation(image)

                        seg.to_JPG(resized_original_image, os.path.join(image_folder, 'Processed', f'{index+1}-{number}_{root}_original{ext}'))
                        
                        masks = {key: seg.returned(original_image, image, box) for key, image in masks.items()}
                        masks = {key: size_regurizer(image) for key, image in masks.items()}

                        clean_mask = Cleaning_contour()
                        cleaned_masks = {}
                        for input in masks :
                            clean_contour = clean_mask.clean_contour(masks[input])
                            arc_contour = clean_mask.arc_contour(clean_contour)
                            decay_contour = clean_mask.decay_contour(arc_contour) 
                            cleaned_masks[input] = decay_contour

                            output_path = os.path.join(image_folder, 'Processed', f'{index+1}-{number}_{root}_{input}{ext}')
                            seg.to_JPG(cleaned_masks[input],output_path)
                        

                        post_data = Post_processing(cleaned_masks)
                        data = post_data.postProcess()


                        file_path = os.path.join(image_folder, 'Processed', f'{index+1}-{number}_{root}_postline.json')
                        with open(file_path, 'w') as json_file:
                            json.dump(data, json_file, cls=NumpyEncoder, indent=4)
                            
                        writer.writerow({key:f'{root}_{number}'if key==f'image_name' else 'n/a' for key in fieldnames})
                        
                        number += 1
                        count += 1
                        file.progress = (count / image_number) * 100
                        db.session.commit()

        file.status = 'completed'
        db.session.commit()
        print('Batch inference completed successfully for the selected file.')

    except:
        file.status = 'failed'
        db.session.commit()
        print(f"Error processing file: {e}")
        
    # return redirect(url_for('file', project_number=project_id))

if __name__ == '__main__':
    app.run(debug=False)