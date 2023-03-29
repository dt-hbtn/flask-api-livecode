#!/usr/bin/python3

# flask classes, globals
from flask import Flask, request

# flask auth extension
from flask_httpauth import HTTPBasicAuth

# for JSON serialization/deserialization
import json

# pre-built password-generation functionality
from sha256 import generate_salt, hash_password, hash_matches

# pre-built chord-generation functionality
from chordgen import chord_gen, chord_symbol

# Authorized users (typically would be in db)
_users = {
    'dt-hbtn': {
        'hash': '90429857f4d3d8e7e4f10440b8c7f8d0b36fe708701f879a0c5fb9195da63875',
        'salt': '0321663e9638dbbdb8b8be8e064f8d03'
    }
}

# Step 1. Initialize 'Flask' object

api = Flask(__name__)

# Step 2. Implement basic auth scheme

auth = HTTPBasicAuth()

@auth.verify_password
def verify_password(username: str, password: str) -> str:
    if username in _users:
        salt = _users[username]['salt']
        hashed_pass = _users[username]['hash']
        
        if hash_matches(hashed_pass, password, salt):
            return username
    
    return None

# Step 3. Implement /api/status (GET)

@api.route('/api/status', methods=['GET'])
@auth.login_required
def get_status():
    response = {'status': 'chordgen API is up and running!'}
    return json.dumps(response)

# Step 4. Implement /api/generate (POST)

@api.route('/api/generate', methods=['POST'])
@auth.login_required
def generate_chord():
    body = json.loads(request.data)
    root = body['root']
    quality = body['quality']
    extensions = body['extensions']
    
    pitches = chord_gen(root, quality, extensions)
    symbol = chord_symbol(root, quality, extensions)
    
    response = {
        'chordSymbol': symbol,
        'pitches': pitches
    }
    
    return json.dumps(response)
