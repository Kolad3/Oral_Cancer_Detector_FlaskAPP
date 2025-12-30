import os 
os.environ['TF_USE_LEGACY_KERAS'] = '1'  # Ensure compatibility with certain TensorFlow versions

class Config:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__)) # Using absolute paths so Flask doesn't get lost 
    MODEL_PATH = os.path.join(BASE_DIR, 'models', 'model.h5')

    SECRET_KEY = os.environ.get('SECRET_KEY') or 'super-secret-dev-key'