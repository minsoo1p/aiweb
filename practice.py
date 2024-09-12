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

from datetime import datetime

from flask import Flask, render_template, redirect, url_for, request, flash, jsonify, send_from_directory, flash, send_file
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
from kind_detection import Preprocessing
import matplotlib.pyplot as plt


import cv2
import matplotlib.pyplot as plt

def visualize_single_box_on_image(image, box, score=None, class_id=None):
    """
    원본 이미지에 선택된 단일 바운딩 박스를 그리는 함수
    :param image: 원본 이미지 (NumPy 배열)
    :param box: 단일 바운딩 박스 좌표
    :param score: 감지된 객체의 신뢰도 점수
    :param class_id: 감지된 객체의 클래스 ID
    :return: 바운딩 박스가 그려진 이미지
    """
    image_copy = image.copy()  # 원본 이미지를 복사하여 수정

    # 박스 좌표 추출
    x1, y1, x2, y2 = box
    
    # 바운딩 박스 그리기 (파란색, 두께 2)
    cv2.rectangle(image_copy, (x1, y1), (x2, y2), (255, 0, 0), 2)

    # 클래스와 신뢰도 점수 표시
    label = f"Class: {int(class_id)}" if class_id is not None else ""
    if score is not None:
        label += f" ({score:.2f})"
    cv2.putText(image_copy, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

    return image_copy

# 예시로 사용할 이미지 경로 (여기에 실제 경로를 넣어주세요)
image_path = 'static/images/double_vertical.jpg'
image_path = 'static/image/05807cdb-a7f1-4859-a129-18be35d3a6b8/5L.JPG'


image = cv2.imread(image_path)  # 이미지 로드

# YOLO 모델을 통해 바운딩 박스를 감지
seg = foot_lateral_segmentation('static/models/kind_detection_yolov8_model.pt', 'cal')
results = seg.detect_and_crop(image)

print(len(results))

# # YOLO의 결과로부터 바운딩 박스 좌표와 클래스 정보 가져오기
# boxes = [result['box'] for result in results]
# classes = [result['type'] for result in results]
# scores = [result['score'] for result in results] if 'score' in results[0] else None  # 만약 YOLO 결과에 score가 있을 경우

# # 두 번째 박스만 선택
# if len(boxes) > 1:  # 두 번째 박스가 있는지 확인
#     box = boxes[1]  # 두 번째 박스
#     class_id = classes[1]  # 두 번째 박스의 클래스 ID
#     score = scores[1] if scores is not None else None  # 두 번째 박스의 신뢰도 점수 (존재하는 경우)

#     # 두 번째 바운딩 박스를 원본 이미지에 그리기
#     output_image = visualize_single_box_on_image(image, box, score, class_id)

#     # 이미지를 matplotlib으로 시각화
#     plt.figure(figsize=(10, 10))
#     plt.imshow(cv2.cvtColor(output_image, cv2.COLOR_BGR2RGB))  # OpenCV는 BGR 형식이므로 RGB로 변환
#     plt.axis('off')
#     plt.show()
# else:
#     print("두 번째 바운딩 박스가 없습니다.")

