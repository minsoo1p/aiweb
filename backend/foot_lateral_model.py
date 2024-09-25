from keras.models import load_model
import numpy as np
import matplotlib.pyplot as plt
from image_processing import Process

model_path_tib = 'static/models/tib_model.h5'
model_path_tal = 'static/models/tal_model.h5'
model_path_cal = 'static/models/cal_model.h5'
model_path_m1 = 'static/models/m1_model.h5'
model_path_m5 = 'static/models/m5_model.h5'
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

#path = 'static/image/436b6c8b-e25b-4b01-98cc-c0d18dd2acc8'

#seg = foot_lateral_segmentation()
#images = seg.preprocess(path)
#seg.segmentation(images[1],'tal')







# Load an example image
#image = images[1]  # Change this to your input image
#image = np.expand_dims(image, axis=0)  # Add batch dimension

# Predict the mask
#predicted_mask = model_cal.predict(image)
#predicted_mask = (predicted_mask > 0.5).astype(np.uint8)  # Binarize the output
#predicted_mask = predicted_mask[0, :, :, 0]

#plt.imshow(predicted_mask, cmap='gray')
#plt.show()
