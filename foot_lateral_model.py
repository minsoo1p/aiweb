from keras.models import load_model
import numpy as np
import matplotlib.pyplot as plt
from image_processing import Process

model_path_tib = 'static/models/model_tib.h5'
model_path_tal = 'static/models/model_tal.h5'
model_path_cal = 'static/models/model_cal.h5'
model_path_m1 = 'static/models/model_m1.h5'
model_path_m5 = 'static/models/model_m5.h5'
models = {
    'tib' : model_path_tib,
    'tal' : model_path_tal,
    'cal' : model_path_cal,
    'm1' : model_path_m1,
    'm5' : model_path_m5,
}


# model_cal = load_model(model_path_tal)


class foot_lateral_segmentation :
    def __init__(self) -> None:
        pass
    
    def preprocess(self, path) :
        process = Process()
        images = process.load_images(path)
        return images

    def segmentation(self, image, model) : 
        model_path = models[model]
        model = load_model(model_path)
        image = np.expand_dims(image, axis=0)  # Add batch dimension

        # Predict the mask
        predicted_mask = model.predict(image)
        predicted_mask = (predicted_mask > 0.5).astype(np.uint8)  # Binarize the output
        predicted_mask = predicted_mask[0, :, :, 0]

        plt.imshow(predicted_mask, cmap='gray')
        plt.show()

# path = 'static/image/846546c3-d0f5-4a2a-9750-a25cdfd50eee'

# seg = foot_lateral_segmentation()
# images = seg.preprocess(path)
# seg.segmentation(images[1],'tal')







'''
# Load an example image
image = images[1]  # Change this to your input image
image = np.expand_dims(image, axis=0)  # Add batch dimension

# Predict the mask
predicted_mask = model_cal.predict(image)
predicted_mask = (predicted_mask > 0.5).astype(np.uint8)  # Binarize the output
predicted_mask = predicted_mask[0, :, :, 0]

plt.imshow(predicted_mask, cmap='gray')
plt.show()
'''
