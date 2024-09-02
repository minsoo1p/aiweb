import tensorflow as tf

import cv2
import numpy as np
from PIL import Image, ImageOps
import base64
from io import BytesIO
import json
import csv

import re
import os
import json
import shutil
from dotenv import load_dotenv
import uuid
from werkzeug.utils import secure_filename

from datetime import datetime

from flask import Flask, render_template, redirect, url_for, request, flash, jsonify, send_from_directory, flash
from flask_bootstrap import Bootstrap5
from flask_socketio import SocketIO, emit
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
from image_processing import Process
from post_processing import Cleaning_contour, Post_processing

load_dotenv() 

app = Flask(__name__)
app_key = os.getenv('APP_KEY')
hash_method = os.getenv('HASH')
salt = int(os.getenv('SALT'))
socketio = SocketIO(app)
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
    status = db.Column(db.String, default='pending')
    
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


def pad_image_to_square(input_image, target_size=512):
    # 원본 이미지 크기 가져오기
    width, height = input_image.size

    # 이미지가 정사각형이 아니면 패딩 추가
    if width != height:
        # 패딩 계산
        delta_w = target_size - width
        delta_h = target_size - height
        padding = (delta_w // 2, delta_h // 2, delta_w - (delta_w // 2), delta_h - (delta_h // 2))

        # 패딩 추가하여 이미지 정사각형 만들기
        input_image = ImageOps.expand(input_image, padding, fill=(0, 0, 0))

    # 512x512로 크기 조정
    output_image = input_image.resize((target_size, target_size), Image.ANTIALIAS)

    return output_image

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
        unique_folder_name = str(uuid.uuid4())
        folder_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_folder_name)
        os.makedirs(os.path.join(folder_path, 'Processed'), exist_ok=True)
        for image in images:
            image_path = os.path.join(folder_path, image.filename)
            image.save(image_path)

        new_file = File(name1=Name1, name2=Name2, image_data=unique_folder_name, image_number=len(images) ,file_time=current_date, project_id=project_number)
        db.session.add(new_file)
        db.session.commit()
        files = File.query.filter_by(project_id=project_number).all()
        data_tables = db.relationship('DataTable', backref='file', lazy=True)

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




# def load_and_process_images(image_folder, target_size=(512, 512)):
#     processed_images = []
#     image_filenames = sorted(os.listdir(image_folder))

#     for image_filename in image_filenames:
#         if image_filename.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
#             image_path = os.path.join(image_folder, image_filename)
#             image = cv2.imread(image_path)
#             if image is None:
#                 print(f"Error reading image: {image_filename}")
#                 continue

#             processed_image = resize_and_pad(image, target_size)
#             processed_images.append(processed_image)
#     return processed_images

# def image_to_base64(image):
#     _, buffer = cv2.imencode('.png', image)
#     img_str = base64.b64encode(buffer).decode('utf-8')
#     return f"data:image/png;base64,{img_str}"

def model_inference(original_image_path, segmented_output_path):
    """
    # AI 모델 돌아가고 segmentation 결과물을 저장하는 함수
    # 
    # image = load_image(original_image_path)
    # segmented_image = run_segmentation_model(image)
    # save_image(segmented_image, segmented_output_path)
    """
    #dummy function
    # os.makedirs(segmented_output_path, exist_ok=True)
    # file_base = os.path.basename(original_image_path)
    # file_name = os.path.splitext(file_base)[0]
    # dummy_path = f'tmp/{file_name}_segmented'

    # if os.path.exists(dummy_path):
    #     for item in os.listdir(dummy_path):
    #         s = os.path.join(dummy_path, item)
    #         d = os.path.join(segmented_output_path, item)
            
    #         shutil.copy2(s, d)
            
    #     print('dummy segmentation folder was made.')
    
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
    #dummy function
    # os.makedirs(line_objects_output_path, exist_ok=True)
    # dummy_path = f'tmp/line_objects.json'
    # if os.path.exists(dummy_path):
    #     shutil.copy2(dummy_path, os.path.join(line_objects_output_path, 'line_objects.json'))
        
    #     print('dummy line_objects folder was made.')
    
    pass

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
    for img in sorted(os.listdir(processed_folder)):
        if img.lower().endswith(('original.png', 'original.jpg', 'original.jpeg')):
            index = int(img.split('_')[0])
            preprocessed_images[index] = url_for('static', filename=f'image/{file.image_data}/Processed/{img}')

    # preprocessed_images = [url_for('static', filename=f'image/{file.image_data}/Processed/{img}') 
    #                     for img in sorted(os.listdir(os.path.join(folder_path, 'Processed')), key=lambda file: int(file.split('_')[0])) 
    #                     if img.lower().endswith(('original.png', 'original.jpg', 'original.jpeg'))]

    
    # processed_original_images = load_and_process_images(original_images)
    # processed_segmented_images = load_and_process_images(segmented_images)
    
    # visualized_original_images = [image_to_base64(img) for img in processed_original_images]
    # visualized_segmented_images = [image_to_base64(img) for img in processed_segmented_images]

    segmented_images = {}
    # for img_folder in sorted(os.listdir(folder_path)):
    #     img_path = os.path.join(folder_path, img_folder)
    #     if os.path.isdir(img_path):
    #         segmented_images[img_folder] = [
    #             url_for('static', filename=f'image/{file.image_data}/{img}')
    #             for img in sorted(os.listdir(img_path))
    #             if img.lower().endswith(('.png', '.jpg', '.jpeg'))
    #         ]
    
    for img in sorted(os.listdir(processed_folder)):
        if img.lower().endswith(('.png', '.jpg', '.jpeg')) and not img.lower().endswith(('_original.png', '_original.jpg', '_original.jpeg')):
            root, ext = os.path.splitext(img)
            parts = root.split('_')
            if len(parts) > 2:
                index = int(parts[0])
                original_name = '_'.join(parts[1:-1])
                seg_type = parts[-1]
                if index not in segmented_images:
                    segmented_images[index] = {}
                    segmented_images[index]['name'] = original_name
                segmented_images[index][seg_type] = url_for('static', filename=f'image/{file.image_data}/Processed/{img}')

            
    line_objects = {}
    for lines in sorted(os.listdir(processed_folder)):
        if lines.lower().endswith('.json'):
            root, ext = os.path.splitext(lines)
            parts = root.split('_')
            index = int(parts[0])
            original_name = '_'.join(parts[1:-1])
            with open(os.path.join(processed_folder, lines), 'r') as f:
                try:
                    line_objects[index] = {
                        'name': original_name,
                        'content': json.load(f)
                    }
                except json.JSONDecodeError:
                    print(f"Error decoding JSON file: {lines}")
                    line_objects[root] = {}
                    
    # Read angle data from CSV
    csv_file_path = os.path.join(processed_folder, 'angles.csv')
    angle_data = []
    if os.path.exists(csv_file_path):
        with open(csv_file_path, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            angle_data = list(reader)

    return render_template('processing.html', 
                           projects=projects, 
                           file=file, 
                           original_images=preprocessed_images,
                           segmented_images=segmented_images, 
                           line_objects=json.dumps(line_objects),
                           angle_data=angle_data)

# # Processing page에서 'save and export data' 버튼 누르면 변경된 데이터를 저장
# @app.route("/save_data_table", methods=['POST'])
# @login_required
# def save_data_table():
#     data = request.json
#     for row in data:
#         data_table = DataTable.query.filter_by(image_name=row['image_name']).first()
#         for key, value in row.items():
#             if key != ('id' or 'image_name') and hasattr(data_table, key):
#                 setattr(data_table, key, value)
#     db.session.commit()
#     return jsonify({"success": True})

# @app.route("/angles", methods=['GET', 'POST'])
# def angles():
#     return render_template('angles.html')

class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        return super(NumpyEncoder, self).default(obj)

@socketio.on('connect')
def test_connect():
    emit('my response', {'data': 'Connected'})

@tf.function
@login_required    
@socketio.on('start_inference')
def batch_inference(data):
    project_id = data['project_id']
    file_id = data['file_id']
    file = File.query.get(file_id)
    
    if file and file.project_id == project_id:
        try:
            image_folder = os.path.join(app.config['UPLOAD_FOLDER'], file.image_data)
            seg = foot_lateral_segmentation('m1', 'm5', 'cal', 'tal', 'tib')
            #total processing count
            image_number = len([f for f in os.listdir(image_folder) if f.endswith(('.png', '.jpg', '.jpeg', '.PNG', '.JPG', '.JPEG'))])
            total_process = image_number * 7
            count = 0
            file.status = 'processing'
            db.session.commit()
            
            #CSV creation
            fieldnames = ['image_name', 'tibioCalaneal', 'taloCalcaneal', 'calcanealPitch', 'Meary']
            csv_file_path = os.path.join(image_folder, 'Processed', f'angles.csv')
            with open(csv_file_path, 'w', newline='') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                for index, image_file in enumerate(sorted(os.listdir(image_folder))):
                    if image_file.lower().endswith(('.png', '.jpg', '.jpeg', '.PNG', '.JPG', '.JPEG')):
                        full_image_path = os.path.join(image_folder, image_file)
                        image = Image.open(full_image_path)
                        root, ext = os.path.splitext(image_file)
                        image = seg.preprocess(full_image_path)
                        original, masks = seg.segmentation(image)

                        seg.to_JPG(original, os.path.join(image_folder, 'Processed', f'{index+1}_{root}_original{ext}'))
                        count += 1
                        socketio.emit('inference_progress', {'file_id': file_id, 'progress': round(count/total_process * 100, 1)})
                        
                        clean_mask = Cleaning_contour()
                        cleaned_masks = {}
                        for input in masks :
                            clean_contour = clean_mask.clean_contour(masks[input])
                            arc_contour = clean_mask.arc_contour(clean_contour)
                            decay_contour = clean_mask.decay_contour(arc_contour) 
                            cleaned_masks[input] = decay_contour

                            output_path = os.path.join(image_folder, 'Processed', f'{index+1}_{root}_{input}{ext}')
                            seg.to_JPG(cleaned_masks[input],output_path)
                            count += 1
                            socketio.emit('inference_progress', {'file_id': file_id, 'progress': round(count/total_process * 100, 1)})

                        post_data = Post_processing(cleaned_masks)
                        data = post_data.postProcess()
                        count += 1
                        socketio.emit('inference_progress', {'file_id': file_id, 'progress': round(count/total_process * 100, 1)})

                        file_path = os.path.join(image_folder, 'Processed', f'{index+1}_{root}_postline.json')
                        with open(file_path, 'w') as json_file:
                            json.dump(data, json_file, cls=NumpyEncoder, indent=4)
                            
                        writer.writerow({
                            'image_name': f'{index+1}.{root}',
                            'tibioCalaneal': 'n/a',
                            'taloCalcaneal': 'n/a',
                            'calcanealPitch': 'n/a',
                            'Meary': 'n/a'
                        })
            
            file.status = 'completed'
            db.session.commit()
            socketio.emit('inference_complete', {'file_id': file_id, 'status': 'completed'})
            # file.inference_complete = True
            # db.session.commit()
            
            print('Batch inference completed successfully for the selected file.')
            
        except Exception as e:
            print(f"Error processing image: {e}")
            file.status = 'failed'
            db.session.commit()
            emit('inference_complete', {'file_id': file_id, 'status': 'failed'})
    else:
        print('Invalid file or permission denied.')
    
    return redirect(url_for('file', project_number=project_id))

if __name__ == '__main__':
    app.run(debug=True)