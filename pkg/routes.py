import os 
os.environ['TF_USE_LEGACY_KERAS'] = '1'  # Ensure compatibility with certain TensorFlow versions
from pkg import app 
from flask import request, jsonify, render_template
import tf_keras as keras
from pkg.utils import model, preprocess_image



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
