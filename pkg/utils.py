import numpy as np
from PIL import Image, ImageStat
from tf_keras.preprocessing.image import img_to_array
from tf_keras import backend as K
from pkg.config import Config
from tf_keras.models import load_model

def f1_score_metric(y_true, y_pred):
    '''
        Custom F1 Score Metric for model loading
    '''
    from tf_keras import backend as K
    y_pred_binary = K.round(y_pred) 
    tp = K.sum(K.cast(y_true * y_pred_binary, 'float'), axis=0)
    fp = K.sum(K.cast((1 - y_true) * y_pred_binary, 'float'), axis=0)
    fn = K.sum(K.cast(y_true * (1 - y_pred_binary), 'float'), axis=0)
    precision = tp / (tp + fp + K.epsilon())
    recall = tp / (tp + fn + K.epsilon())
    f1 = 2 * (precision * recall) / (precision + recall + K.epsilon())

    
    return f1

custom_objects_dict = {'f1_score_metric': f1_score_metric}
model = load_model(Config.MODEL_PATH, custom_objects=custom_objects_dict)

def preprocess_image(image_file): 
    '''
        Resizes and formats image for the model
    '''
    target_size = (224, 224)

    img = Image.open(image_file)
    if img.mode != 'RGB':
        img = img.convert('RGB')

    img = img.resize(target_size)
    img_array = img_to_array(img)
    # img_array = img_array / 255.0
    img_array = np.expand_dims(img_array, axis=0)

    return img_array