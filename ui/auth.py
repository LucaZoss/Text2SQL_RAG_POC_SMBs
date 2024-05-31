import firebase_admin
from firebase_admin import auth
from flask import request, jsonify

def verify_id_token(token):
    try:
        decoded_token = auth.verify_id_token(token)
        return decoded_token
    except Exception as e:
        print(e)
        return None