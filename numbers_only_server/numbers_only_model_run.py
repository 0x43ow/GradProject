import tensorflow as tf
from generator import get_captcha_image
from PIL import Image

import numpy as np # linear algebra

tf.__version__
model = tf.keras.models.load_model('numbers_only_model.h5')

# Check its architecture
model.summary()

def format_y(y):
    return ''.join(map(lambda x: chr(int(x)), y))


def predict(image_path):
    """
    given captcha image, returns the model's predictions
    """
    im = Image.open(image_path).convert('RGB').resize((120, 100))
    im = np.array(im) / 255.0
    im = np.array(im)
    
    y_pred = model.predict(np.array([im]))
    y_pred = tf.math.argmax(y_pred, axis=-1)   
    return format_y(y_pred[0])


