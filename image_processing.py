import numpy as np
import cv2
import os
import matplotlib.pyplot as plt
from keras.utils import to_categorical

import numpy as np
import cv2

class Process : 
    def __init__(self) -> None:
        pass

    def preprocess_image (self, image,target_size=(512, 512)):
        if image is None == 0:
            print("Error: image are None or empty")
            return None, None

        if len(image.shape) == 3:
            if image.shape[-1] > 1:
                gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                gray_image = image.squeeze()
        else:
            gray_image = image

        contours_image, _ = cv2.findContours(gray_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if len(contours_image) == 0:
            resized_image = cv2.resize(image, target_size)
            gray_resized_image = cv2.cvtColor(resized_image, cv2.COLOR_BGR2GRAY) if len(resized_image.shape) == 3 else resized_image
            return np.expand_dims(gray_resized_image, axis=-1)

        largest_contour = max(contours_image, key=cv2.contourArea)
        x, y, w, h = cv2.boundingRect(largest_contour)

        if w < 20 or h < 20 or w / h > 10 or h / w > 10:
            print("Warning: Abnormal bounding rectangle detected.")
            resized_image = cv2.resize(image, target_size)
            gray_resized_image = cv2.cvtColor(resized_image, cv2.COLOR_BGR2GRAY) if len(resized_image.shape) == 3 else resized_image
            return np.expand_dims(gray_resized_image, axis=-1)

        cropped_image = image[y:y+h, x:x+w]

        height, width = cropped_image.shape[:2]
        if height > width:
            padding = (height - width) // 2
            square_image = cv2.copyMakeBorder(cropped_image, 0, 0, padding, padding, cv2.BORDER_CONSTANT, value=[0, 0, 0])
        elif width > height:
            padding = (width - height) // 2
            square_image = cv2.copyMakeBorder(cropped_image, padding, padding, 0, 0, cv2.BORDER_CONSTANT, value=[0, 0, 0])
        else:
            square_image = cropped_image

        resized_image = cv2.resize(square_image, target_size)
        gray_resized_image = cv2.cvtColor(resized_image, cv2.COLOR_BGR2GRAY) if len(resized_image.shape) == 3 else resized_image

        return np.expand_dims(gray_resized_image, axis=-1)

    def load_images (self, image_path, target_size=(512, 512)):
        image = cv2.imread(image_path)
        if image is None:
            print(f"Error reading image: {image_path}")

        processed_image = self.preprocess_image (image, target_size)
        if processed_image is not None :
            if len(processed_image.shape) == 2:  # 그레이스케일 이미지인 경우
                processed_image = np.expand_dims(processed_image, axis=-1)  # 채널 차원을 추가하여 (512, 512, 1)로 만듦

        images_array = np.array(processed_image)
        return images_array

# path = 'static/image/f7048e8e-0f9d-499b-905c-08bd191d0798/KakaoTalk_20240807_213239161_01.jpg'
# process = Process()
# images = process.load_images(path)




