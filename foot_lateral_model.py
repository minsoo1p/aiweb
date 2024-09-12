from keras.models import load_model
import numpy as np
import matplotlib.pyplot as plt
from image_processing import Process
from kind_detection import Preprocessing
from post_processing import Cleaning_contour, Post_processing
from PIL import Image
from concurrent.futures import ThreadPoolExecutor, as_completed
import os

import cv2
from ultralytics import YOLO
import numpy as np
from shapely.geometry import box

def custom_nms(boxes, scores, classes, iou_threshold=0.1):
    order = scores.argsort()[::-1]
    keep = []
    while order.size > 0:
        i = order[0]
        keep.append(i)
        if order.size == 1:
            break
        ious = np.array([compute_iou(boxes[i], boxes[j]) for j in order[1:]])
        inds = np.where(ious <= iou_threshold)[0]
        order = order[inds + 1]
    return keep

def compute_iou(box1, box2):
    poly1 = box(*box1)
    poly2 = box(*box2)
    intersection = poly1.intersection(poly2).area
    union = poly1.union(poly2).area
    return intersection / union if union > 0 else 0

# yolo_model_path = 'static\models\kind_detection_yolov8_model.pt'

# model_path_tib = 'static/models/foot/tib_model.h5'
# model_path_tal = 'static/models/foot/tal_model.h5'
# model_path_cal = 'static/models/foot/cal_model.h5'
# model_path_m1 = 'static/models/foot/m1_model.h5'
# model_path_m5 = 'static/models/foot/m5_model.h5'
# models = {
#     'tib' : model_path_tib,
#     'tal' : model_path_tal,
#     'cal' : model_path_cal,
#     'm1' : model_path_m1,
#     'm5' : model_path_m5,
# }


# def load_model_thread(model_name):
#     return model_name, load_model(models[model_name])


class foot_lateral_segmentation :
    def __init__(self, yolo_model_path, *input_models):
        self.models = {}  # Keras 모델 저장
        self.yolo_model = None  # YOLO 모델 초기화

        # 병렬로 YOLO 및 Keras 모델을 동시에 로드
        with ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
            futures = []

            # YOLO 모델 로드 병렬 작업 추가
            futures.append(executor.submit(self.load_yolo_model, yolo_model_path))

            # Keras 모델 로드 병렬 작업 추가
            for model_name in input_models:
                futures.append(executor.submit(self.load_model_thread, model_name))

            # 병렬 작업 결과 처리
            for future in as_completed(futures):
                result = future.result()
                if isinstance(result, tuple):
                    model_name, loaded_model = result
                    self.models[model_name] = loaded_model
                else:
                    # YOLO 모델이 로드된 경우
                    self.yolo_model = result

        self.max_workers = min(len(self.models), os.cpu_count() or 1)

    def load_yolo_model(self, yolo_model_path):
        return YOLO(yolo_model_path)

    def load_model_thread(self, model_name):
        model_path = {
            'tib': 'static/models/foot/tib_model.h5',
            'tal': 'static/models/foot/tal_model.h5',
            'cal': 'static/models/foot/cal_model.h5',
            'm1': 'static/models/foot/m1_model.h5',
            'm5': 'static/models/foot/m5_model.h5',
        }
        return model_name, load_model(model_path[model_name])

    def preprocess(self, path) :
        process = Process()
        images = process.load_images(path)
        images = images.astype('float32') / 255.0
        images = np.array(images)
        return images

    def predict_mask(self, model_name, model, image):
        predicted_mask = model.predict(image)
        predicted_mask = (predicted_mask > 0.5).astype(np.uint8)  # Binarize the output
        return model_name, predicted_mask[0, :, :, 0]

    def segmentation(self, image):
        image = np.expand_dims(image, axis=0)  # Add batch dimension

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = [executor.submit(self.predict_mask, model_name, model, image)
                       for model_name, model in self.models.items()]

            predicted_masks = {}
            for future in as_completed(futures):
                model_name, mask = future.result()
                predicted_masks[model_name] = mask

        original_image = image[0, :, :, 0]  # 배치 차원 제거

        return original_image, predicted_masks

    def to_JPG(self, image_array, path) :
        if np.max(image_array) <= 1.0:
            image_array = (image_array * 255).astype(np.uint8)
        else:
            image_array = image_array.astype(np.uint8)
        image = Image.fromarray(image_array)
        image.save(path, format='PNG')




    def detect_and_crop(self, image):
        result = self.yolo_model(image)[0]
        boxes = result.boxes.xyxy.cpu().numpy().astype(int)
        scores = result.boxes.conf.cpu().numpy()
        classes = result.boxes.cls.cpu().numpy()

        score_mask = scores >= 0.5
        boxes = boxes[score_mask]
        scores = scores[score_mask]
        classes = classes[score_mask]

        if len(scores) > 0:
            # 커스텀 NMS 적용
            keep = custom_nms(boxes, scores, classes, iou_threshold=0.1)

            # 선택된 박스, 점수, 클래스만 유지
            filtered_boxes = boxes[keep]
            filtered_scores = scores[keep]
            filtered_classes = classes[keep]
        else:
            filtered_boxes = np.array([])
            filtered_scores = np.array([])
            filtered_classes = np.array([])

        image_copy = image.copy()
        cropped_results = []

        for box, cls in zip(filtered_boxes, filtered_classes):
            class_id = int(cls)

            x1, y1, x2, y2 = box
            cropped_image = image_copy[y1:y2, x1:x2]
            height, width = cropped_image.shape[:2]
            if height > width:
                padding = (height - width) // 2
                square_image = cv2.copyMakeBorder(cropped_image, 0, 0, padding, padding, cv2.BORDER_CONSTANT, value=[0, 0, 0])
            elif width > height:
                padding = (width - height) // 2
                square_image = cv2.copyMakeBorder(cropped_image, padding, padding, 0, 0, cv2.BORDER_CONSTANT, value=[0, 0, 0])
            else:
                square_image = cropped_image

            resized_image = cv2.resize(square_image, (512, 512))
            gray_resized_image = cv2.cvtColor(resized_image, cv2.COLOR_BGR2GRAY) if len(resized_image.shape) == 3 else resized_image
            gray_resized_image = np.expand_dims(gray_resized_image, axis=-1)

            normalized_image = gray_resized_image.astype('float32') / 255.0
            cropped_results.append({
                'image': normalized_image,
                'box': box,
                'type': class_id
            })

        return cropped_results

    def returned(self, original_image, mask, box):
        black_image = np.zeros_like(original_image[:, :, 0])
        # black_image = np.zeros((512, 512), dtype=np.uint8)

        x1, y1, x2, y2 = box
        box_height = y2 - y1
        box_width = x2 - x1

        mask_size = mask.shape[0]  # 512
        aspect_ratio = box_width / box_height
        if aspect_ratio > 1:
            crop_height = int(mask_size / aspect_ratio)
            crop_width = mask_size
            start = (mask_size - crop_height) // 2
            cropped_mask = mask[start:start+crop_height, :]
        else:
            crop_height = mask_size
            crop_width = int(mask_size * aspect_ratio)
            start = (mask_size - crop_width) // 2
            cropped_mask = mask[:, start:start+crop_width]

        resized_mask = cv2.resize(cropped_mask, (box_width, box_height))
        black_image[y1:y2, x1:x2] = resized_mask
        return black_image


# # 사용하는 방식

# path = 'static\images\KakaoTalk_20240807_213239161_03.jpg'

# seg = foot_lateral_segmentation('cal')
# image = seg.preprocess(path)
# original, masks = seg.segmentation(image)

# clean_mask = Cleaning_contour()
# cleaned_masks = {}
# for input in masks :
#     clean_contour = clean_mask.clean_contour(masks[input])
#     arc_contour = clean_mask.arc_contour(clean_contour)
#     decay_contour = clean_mask.decay_contour(arc_contour) 
#     cleaned_masks[input] = decay_contour



# post_data = Post_processing(cleaned_masks)
# data = post_data.postProcess()

# # 시각화해서 보고 싶다면
# plt.figure(figsize=(10, 5))

# # 첫 번째 subplot에 원본 이미지를 표시합니다.
# plt.subplot(1, 2, 1)
# plt.imshow(original, cmap='gray')
# plt.title('Original Image')
# plt.axis('off')

# # 두 번째 subplot에 예측 마스크를 표시합니다.
# plt.subplot(1, 2, 2)
# plt.imshow(np.array(cleaned_masks['cal']), cmap='gray')
# plt.title('Predicted Mask')
# plt.axis('off')

# # 그림을 화면에 출력합니다.
# plt.show()
# plt.close()




# seg.to_JPG(mask,'aaa')


# path = 'static/image/f7048e8e-0f9d-499b-905c-08bd191d0798/KakaoTalk_20240807_213239161_02.jpg'

# seg = foot_lateral_segmentation()
# image = seg.preprocess(path)
# original, masks = seg.segmentation(image,'m1')

# clean_mask = Cleaning_contour()
# cleaned_masks = {}
# for input in masks :
#     clean_contour = clean_mask.clean_contour(masks[input])
#     arc_contour = clean_mask.arc_contour(clean_contour)
#     decay_contour = clean_mask.decay_contour(arc_contour) 
#     cleaned_masks[input] = decay_contour

# print(original.shape)
# print(masks['m1'].shape)
# print(cleaned_masks['m1'].shape)

# # 시각화해서 보고 싶다면
# plt.figure(figsize=(10, 5))

# # 첫 번째 subplot에 원본 이미지를 표시합니다.
# plt.subplot(1, 2, 1)
# plt.imshow(original, cmap='gray')
# plt.title('Original Image')
# plt.axis('off')

# # 두 번째 subplot에 예측 마스크를 표시합니다.
# plt.subplot(1, 2, 2)
# plt.imshow(cleaned_masks['m1'], cmap='gray')
# plt.title('Predicted Mask')
# plt.axis('off')

# # 그림을 화면에 출력합니다.
# plt.show()

############################################################

# path = 'static\images\double_vertical.jpg'

# seg = foot_lateral_segmentation('cal')
# process = Preprocessing(path)
# results = process.cropping()

# returned_masks = []

# for result in results : 
#   image = result['image']
#   box = result['box']
#   type = result['type']

#   original, masks = seg.segmentation(image)
#   mask = masks['cal']
#   returned_mask = process.returned(mask, box)
#   returned_masks.append(returned_mask)

# plt.subplot(1, 2, 1)
# plt.imshow(returned_masks[0], cmap='gray')
# plt.axis('off')

# plt.subplot(1, 2, 2)
# plt.imshow(returned_masks[1], cmap='gray')
# plt.axis('off')

# plt.show()



