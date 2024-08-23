from keras.models import load_model
import numpy as np
import matplotlib.pyplot as plt
from image_processing import Process
from post_processing import Cleaning_contour, Post_processing
from PIL import Image

model_path_tib = 'static/models/foot/tib_model.h5'
model_path_tal = 'static/models/foot/tal_model.h5'
model_path_cal = 'static/models/foot/cal_model.h5'
model_path_m1 = 'static/models/foot/m1_model.h5'
model_path_m5 = 'static/models/foot/m5_model.h5'
models = {
    'tib' : model_path_tib,
    'tal' : model_path_tal,
    'cal' : model_path_cal,
    'm1' : model_path_m1,
    'm5' : model_path_m5,
}


class foot_lateral_segmentation :
    def __init__(self, *input_models) :
        self.models = {input_model: load_model(models[input_model]) for input_model in input_models}
    
    def preprocess(self, path) :
        process = Process()
        images = process.load_images(path)
        images = images.astype('float32') / 255.0 
        images = np.array(images)
        return images

    def segmentation(self, image) : 
        predicted_masks = {}
        image = np.expand_dims(image, axis=0)  # Add batch dimension

        for input_model in self.models : 
          model = self.models[input_model]
          # Predict the mask
          predicted_mask = model.predict(image)
          predicted_mask = (predicted_mask > 0.5).astype(np.uint8)  # Binarize the output
          predicted_mask = predicted_mask[0, :, :, 0]
          predicted_masks[input_model] = predicted_mask

        original_image = image[0, :, :, 0]  # 배치 차원 제거

        return original_image, predicted_masks
    
    def to_JPG(self, image_array, path) : 
        if np.max(image_array) <= 1.0:
            image_array = (image_array * 255).astype(np.uint8)
        else:
            image_array = image_array.astype(np.uint8)
        image = Image.fromarray(image_array)
        image.save(path, format='JPEG')


# # 사용하는 방식

# path = 'static/image/f7048e8e-0f9d-499b-905c-08bd191d0798/KakaoTalk_20240807_213239161_02.jpg'

# seg = foot_lateral_segmentation('m1', 'tib', 'tal', 'm5')
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
# print(data)


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





