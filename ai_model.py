# File: ai_model.py (Sahi Code)
import tensorflow as tf
from tensorflow.keras.applications.mobilenet_v2 import MobileNetV2, preprocess_input, decode_predictions
from tensorflow.keras.preprocessing import image
import numpy as np

model = MobileNetV2(weights='imagenet')

def predict_image(image_path):
    img = image.load_img(image_path, target_size=(224, 224))
    img_array = image.img_to_array(img)
    img_array_expanded = np.expand_dims(img_array, axis=0)
    processed_img = preprocess_input(img_array_expanded)
    predictions = model.predict(processed_img)
    decoded_predictions = decode_predictions(predictions, top=3)[0]
    return decoded_predictions