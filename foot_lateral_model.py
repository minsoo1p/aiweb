from keras.models import load_model
import numpy as np
import matplotlib.pyplot as plt
from image_processing import Process
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

def change(inputs, color):
  arr_rgb = np.concatenate((inputs, inputs, inputs), axis=2) # 3번째 차원의 길이를 1에서 3으로 늘이기
  x=inputs.shape[0]
  y=inputs.shape[1]
  for i in range(0,x):
    for j in range(0,y):
      if arr_rgb[i][j].all():
        arr_rgb[i][j] = color
      else:
        arr_rgb[i][j]= [0,0,0]

  return arr_rgb

# model_cal = load_model(model_path_tal)


class foot_lateral_segmentation :
    def __init__(self) -> None:
        pass
    
    def preprocess(self, path) :
        process = Process()
        images = process.load_images(path)
        images = images.astype('float32') / 255.0 
        images = np.array(images)
        return images

    def segmentation(self, image, model) : 
        model_path = models[model]
        model = load_model(model_path)
        image = np.expand_dims(image, axis=0)  # Add batch dimension

        # Predict the mask
        predicted_mask = model.predict(image)
        predicted_mask = (predicted_mask > 0.5).astype(np.uint8)  # Binarize the output
        predicted_mask = predicted_mask[0, :, :, 0]

        original_image = image[0, :, :, 0]  # 배치 차원 제거

        # 시각화
        fig, axs = plt.subplots(1, 2, figsize=(10, 5))
        axs[0].imshow(original_image, cmap='gray')
        axs[0].set_title('Original Image')
        axs[1].imshow(predicted_mask, cmap='gray')
        axs[1].set_title('Predicted Mask')
        plt.show()
        

    # def blend(self, original_image, predicted_mask):
    #     color_image = change(predicted_mask, [255, 0, 0])
        
    #     # original_image 값을 255로 변환
    #     original_image = (original_image * 255).astype(np.uint8)
    #     original_image = Image.fromarray(original_image)

    #     # mask 이미지를 RGB로 변환
    #     color_image = Image.fromarray(color_image)

    #     # 블렌딩 이미지 생성
    #     merged_image = Image.blend(original_image.convert('RGBA'), color_image.convert('RGBA'), alpha=0.2)

    #     # 이미지 표시
    #     plt.imshow(merged_image)
    #     plt.axis('off')
    #     plt.title('Blended Masks')
    #     plt.show()



'''
path = 'static/image/846546c3-d0f5-4a2a-9750-a25cdfd50eee'

seg = foot_lateral_segmentation()
images = seg.preprocess(path)
seg.segmentation(images[1],'tal')
'''








