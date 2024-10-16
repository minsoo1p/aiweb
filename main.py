# import tensorflow as tf

import cv2
from cv2 import ximgproc
import numpy as np
from PIL import Image, ImageOps
import base64
from io import BytesIO
import json
import csv
import ast
import asyncio
import aiohttp

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

from post_processing import Cleaning_contour, Post_processing

load_dotenv() 

app = Flask(__name__)
app_key = os.getenv('APP_KEY')
hash_method = os.getenv('HASH')
salt = int(os.getenv('SALT'))
app.config['SECRET_KEY'] = app_key
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///posts.db'
app.config['UPLOAD_FOLDER'] = 'static/image'

# RunPod API 설정
API_ENDPOINT = os.getenv('API_ENDPOINT')
API_KEY = os.getenv('API_KEY')

count = 0
image_number = 0
image_names = []

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
    progress = db.Column(db.Integer, default=0)

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
    for img in sorted(os.listdir(processed_folder),
                      key=lambda x: (
                          int(x.split('_')[0].split('-')[0]) if '_' in x else float('inf'),
                          int(x.split('_')[0].split('-')[1]) if '-' in x.split('_')[0] else 0
                      )):
        if img.lower().endswith(('original.png', 'original.jpg', 'original.jpeg')):
            index = img.split('_')[0]
            preprocessed_images[number] = url_for('static', filename=f'image/{file.image_data}/Processed/{img}')
            number += 1

    segmented_images = {}
    number = 0
    guide = ''
    for img in sorted(os.listdir(processed_folder),
                      key=lambda x: (
                          int(x.split('_')[0].split('-')[0]) if '_' in x else float('inf'),
                          int(x.split('_')[0].split('-')[1]) if '-' in x.split('_')[0] else 0
                      )):
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
    for lines in sorted(os.listdir(processed_folder),
                        key=lambda x: (
                          int(x.split('_')[0].split('-')[0]) if '_' in x else float('inf'),
                          int(x.split('_')[0].split('-')[1]) if '-' in x.split('_')[0] else 0
                      )):
        if lines.lower().endswith('.json'):
            root, ext = os.path.splitext(lines)
            parts = root.split('_')
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
        file.status = 'processing'
        db.session.commit()
        
        asyncio.run(process_images_runpod(file_id))
        
        file.status = 'completed'
        db.session.commit()
        print('Batch inference completed successfully for the selected file.')
        
    except Exception as e:
        file.status = 'failed'
        db.session.commit()
        print(f"Error processing file: {e}")
        
async def process_images_runpod(file_id):
    global count, image_number
    global image_names
    
    file = File.query.get(file_id)
    image_folder = os.path.join(app.config['UPLOAD_FOLDER'], file.image_data)
    csv_file_path = os.path.join(image_folder, 'Processed', f'angles.csv')
    selectedAngles = ast.literal_eval(file.selected_angles)
    fieldnames = ['image_name'] + selectedAngles
    fieldnames = [item.replace("'", "").replace(" ", "_") for item in fieldnames]
    
    image_number = len([f for f in os.listdir(image_folder) if f.endswith(('.png', '.jpg', '.jpeg', '.PNG', '.JPG', '.JPEG'))])
    count = 0    
    
    async with aiohttp.ClientSession() as session:
        tasks = []
        for index, image_file in enumerate(sorted([f for f in os.listdir(image_folder) if f.endswith(('.png', '.jpg', '.jpeg', '.PNG', '.JPG', '.JPEG'))],
                                                  key=lambda x: str(os.path.splitext(x)[0]))):
            task = send_request(session, file_id, index, image_file)
            tasks.append(task)
            
        await asyncio.gather(*tasks)
    
    with open(csv_file_path, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for item in sorted(image_names, key=lambda x: str(x["image_name"])):
            writer.writerow({key: item['image_name'] if key == 'image_name' else 'n/a' for key in fieldnames})
            
    image_names = []
        
async def send_request(session, file_id, index, image_file):
    #variables
    global count, image_number
    file = File.query.get(file_id)
    image_folder = os.path.join(app.config['UPLOAD_FOLDER'], file.image_data)
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
    seglist = list(segset)
        
    image = cv2.imread(os.path.join(image_folder, image_file))
    root, ext = os.path.splitext(image_file)
    
    encoded_array = np_to_base64(image)
    
    #request preparation
    data = {
        "input": {
            "image": encoded_array,
            "shape": image.shape,
            "dtype": str(image.dtype),
            "seglist": seglist
        }
    }
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "authorization": f"Bearer {API_KEY}",
    }

    async with session.post(API_ENDPOINT, headers=headers, json=data) as response:
        if response.status == 200:
            result = await response.json()
            
            shape = result['output']['shape']
            dtype = result['output']['dtype']
            
            if result['output']['num'] == 1:
                #save original image
                resized_original_image = size_regurizer(image)
                to_JPG(resized_original_image, os.path.join(image_folder, 'Processed', f'{index+1}_{root}_original{ext}'))
                
                #get masks from response and decoding
                masks = result['output']['masks'][0]
                masks = {key: base64_to_np(image, shape, dtype) for key, image in masks.items()}

                #clean and save masks
                clean_mask = Cleaning_contour()
                cleaned_masks = {}
                for input in masks :
                    clean_contour = clean_mask.clean_contour(masks[input])
                    arc_contour = clean_mask.arc_contour(clean_contour)
                    decay_contour = clean_mask.decay_contour(arc_contour) 
                    cleaned_masks[input] = decay_contour

                    output_path = os.path.join(image_folder, 'Processed', f'{index+1}_{root}_{input}{ext}')
                    to_JPG(cleaned_masks[input],output_path)
                    
                #postprocessing and save json file                
                post_data = Post_processing(cleaned_masks)
                data = post_data.postProcess()

                file_path = os.path.join(image_folder, 'Processed', f'{index+1}_{root}_postline.json')
                with open(file_path, 'w') as json_file:
                    json.dump(data, json_file, cls=NumpyEncoder, indent=4)
                    
                #add root name for csv creation
                image_names.append({'image_name': root})
                
                #update progress in DB
                count += 1
                file.progress = int((count / image_number) * 100)
                db.session.commit()
                
            elif result['output']['num'] >= 2:
                image_number += (result['output']['num']-1)
                number = 1
                resized_original_image = size_regurizer(image)
                
                masks_list = result['output']['masks']
                for masks in masks_list:
                    #save original image
                    to_JPG(resized_original_image, os.path.join(image_folder, 'Processed', f'{index+1}-{number}_{root}_original{ext}'))
                        
                    #get masks from response and decoding
                    masks = {key: base64_to_np(image, shape, dtype) for key, image in masks.items()}

                    #clean and save masks
                    clean_mask = Cleaning_contour()
                    cleaned_masks = {}
                    for input in masks :
                        clean_contour = clean_mask.clean_contour(masks[input])
                        arc_contour = clean_mask.arc_contour(clean_contour)
                        decay_contour = clean_mask.decay_contour(arc_contour) 
                        cleaned_masks[input] = decay_contour

                        output_path = os.path.join(image_folder, 'Processed', f'{index+1}-{number}_{root}_{input}{ext}')
                        to_JPG(cleaned_masks[input],output_path)
                        
                    #postprocessing and save json file                
                    post_data = Post_processing(cleaned_masks)
                    data = post_data.postProcess()

                    file_path = os.path.join(image_folder, 'Processed', f'{index+1}-{number}_{root}_postline.json')
                    with open(file_path, 'w') as json_file:
                        json.dump(data, json_file, cls=NumpyEncoder, indent=4)
                        
                    #add root name for csv creation
                    image_names.append({'image_name': root})
                    
                    #update progress in DB
                    number += 1
                    count += 1
                    file.progress = int((count / image_number) * 100)
                    db.session.commit()
                
            else:
                raise ValueError("response['num']; out of range")
            
        else:
            print(f"Failed to process image {root}. Status code: {response.status}")
            
            
def np_to_base64(arr):
    arr_bytes = arr.tobytes()
    arr_base64 = base64.b64encode(arr_bytes).decode('utf-8')
    
    return arr_base64

def base64_to_np(encoded_array, shape, dtype):
    arr_bytes = base64.b64decode(encoded_array)
    arr = np.frombuffer(arr_bytes, dtype=dtype).reshape(shape)
    
    return arr

def to_JPG(image_array, path) :
    if np.max(image_array) <= 1.0:
        image_array = (image_array * 255).astype(np.uint8)
    else:
        image_array = image_array.astype(np.uint8)
    image = Image.fromarray(image_array)
    image.save(path, format='PNG')


if __name__ == '__main__':
    app.run(debug=True)