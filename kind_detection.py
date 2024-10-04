import cv2
from ultralytics import YOLO
import numpy as np

# model_path = 'static\models\footLat_detection_yolov8_1_model.pt'
model_path = 'static/models/kind_detection_yolov8_model.pt'
model = YOLO(model_path)
# test_image_path = 'static\images\혼종.jpg' 

def size_regurizer(image_path):
    image = cv2.imread(image_path)
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

class Preprocessing :
  def __init__ (self, image) :
    self.image = image
    self.result = model(self.image)[0]

  def cropping(self):
      result = []

      boxes = self.result.boxes.xyxy.cpu().numpy().astype(int)
      classes = self.result.boxes.cls.cpu().numpy()

      image_copy = self.image.copy()

      for box, cls in zip(boxes, classes):
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

          original_size = max(square_image.shape[:2])
          scale_factor = 512 / original_size

          resized_image = cv2.resize(square_image, (512, 512))
          gray_resized_image = cv2.cvtColor(resized_image, cv2.COLOR_BGR2GRAY) if len(resized_image.shape) == 3 else resized_image
          gray_resized_image = np.expand_dims(gray_resized_image, axis=-1)

          normalized_image = gray_resized_image.astype('float32') / 255.0
          resized_images = {}
          resized_images['image'] = normalized_image
          resized_images['type'] = class_id
          resized_images['box'] = box

          result.append(resized_images)

      return result

  def returned(self, mask, box):
      black_image = np.zeros_like(self.image[:, :, 0])

      x1, y1, x2, y2 = box
      box_height = y2 - y1
      box_width = x2 - x1

      # 마스크를 바운딩 박스의 비율에 맞게 크롭
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

      # 크롭된 마스크를 바운딩 박스 크기로 리사이즈
      resized_mask = cv2.resize(cropped_mask, (box_width, box_height))

      # 리사이즈된 마스크를 black_image에 적용
      black_image[y1:y2, x1:x2] = resized_mask

      return black_image

'''
result = [
  {
    'type' : class_id,
    'box' : box,
    'image' : image
  }, 
  {
    'type' : class_id,
    'box' : box,
    'image' : image
  }
]
'''

