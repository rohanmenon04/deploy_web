from flask import Flask, send_from_directory, render_template, request, jsonify, make_response, session
from flask_compress import Compress
from flask_session import Session
import ssl
import os
import time
import requests

app = Flask(__name__, template_folder='../templates', static_folder='../static_files')
app.secret_key = 'your_secret_key'  # Set a secret key for session management
compress = Compress(app)

# SSL Certificates
app.config['COMPRESS_BR_LEVEL'] = 11
app.config['COMPRESS_GZIP_LEVEL'] = 6

# Configure Flask-Session
app.config['SESSION_TYPE'] = 'filesystem'  # Store sessions in the filesystem
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER'] = True  # To protect the cookie from being tampered
app.config['SESSION_KEY_PREFIX'] = 'myapp_'

# Initialize the session
Session(app)

# Serve the landing page
@app.route('/')
def serve_landing_page():

@app.route('/per-stats')
def serve_per_stats():
    username = session.get('username')  # Retrieve the username from the session
    if not username:
        return "Username not found in session", 400

    backend_url = f'https://backend-service-fag8.onrender.com/api/get-graph-data?username={username}'

    try:
        response = requests.get(backend_url)

@app.route('/save_playerdata', methods=['POST'])
def proxy_save_playerdata():
    data = request.get_json()
    username = data.get('username')
    if username:
        session['username'] = username  # Store the username in the session

    backend_url = 'https://backend-service-fag8.onrender.com/save_playerdata'  # Change to the correct URL and port of your backend server
    try:
        # Forward the request to the backend server
        response = requests.post(backend_url, json=data)
        return jsonify(response.json()), response.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500
def proxy_delete_score():
    data = request.json
    score_to_delete = data.get('score')
    username = session.get('username')  # Retrieve the username from the session

    if not score_to_delete or not username:
        return jsonify({"error": "No score or username provided"}), 400

    backend_url = 'https://backend-service-fag8.onrender.com/api/delete-score'  # Replace with your backend URL

    # Forward the request to the backend
    response = requests.post(backend_url, json={'score': score_to_delete, 'username': username})

    # Return the backend response to the frontend
    return make_response(response.content, response.status_code)

port = int(os.environ.get('PORT', 5000))
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=port, ssl_context=context)
