import firebase_admin
from firebase_admin import credentials

class Config:
    UPLOAD_FOLDER = 'uploads/'
    ALLOWED_EXTENSIONS = {'csv', 'json', 'pdf', 'docx', 'png', 'jpg', 'jpeg'}

    # Initialize Firebase Admin SDK
    cred = credentials.Certificate("path/to/your/firebase/credentials.json")
    firebase_admin.initialize_app(cred)