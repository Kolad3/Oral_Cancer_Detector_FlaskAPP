import os 
os.environ['TF_USE_LEGACY_KERAS'] = '1'  # Ensure compatibility with certain TensorFlow versions
import numpy as np
from PIL import Image, ImageStat
from pkg import app 
from flask import request, jsonify, render_template
import tf_keras as keras
from tf_keras.models import load_model
from tf_keras.preprocessing.image import img_to_array

# Configuration

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
BASE_DIR = os.path.dirname(os.path.abspath(__file__)) # Using absolute paths so Flask doesn't get lost 
MODEL_PATH = os.path.join(BASE_DIR, 'models', 'model.h5')
print('Loading AI Model...')


model = keras.models.load_model(MODEL_PATH, custom_objects=custom_objects_dict)



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

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict/', methods=['POST'])
def predict():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['file']

    try:
        processed_img = preprocess_image(file)        
        prediction = model.predict(processed_img)

        # Interpret result (Adjust logic based on the specific model )
        score = float(prediction[0][0])
        is_cancerous = score > 0.5
        confidence = score if is_cancerous else 1 - score

        if confidence < 0.98:
             return jsonify({
                "status": "success",
                "prediction": "Inconclusive",
                "is_cancerous": False, # Treat as negative for safety
                "confidence_score": confidence,
                "message": "The analysis is inconclusive. The image quality may be low."
            })

        response = {
            "status": "success",
            "prediction": "Cancerous" if is_cancerous else "Healthy", 
            "is_cancerous": bool(is_cancerous),
            "confidence_score": round(confidence, 4)
        }

        return jsonify(response)

    except Exception as e:
        return jsonify({"error": str(e)}), 500
