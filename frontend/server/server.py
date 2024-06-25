from flask import Flask, send_from_directory, render_template, request, jsonify, make_response
from flask_compress import Compress
import ssl
import os
import time
import requests

app = Flask(__name__, template_folder='../templates', static_folder='../static_files')
compress = Compress(app)

# SSL Certificates
context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
context.load_cert_chain(certfile='frontend/server/server.cert', keyfile='frontend/server/server.key')

# Enable Brotli and Gzip compression
app.config['COMPRESS_ALGORITHM'] = ['br', 'gzip']
app.config['COMPRESS_BR_LEVEL'] = 11
app.config['COMPRESS_GZIP_LEVEL'] = 6

# Serve the landing page
@app.route('/')
def serve_landing_page():
    return render_template('landing_page.html')

# Serve static files and set Content-Encoding for Brotli files
@app.route('/WebGLBuilds/<path:filename>')
def serve_webgl_builds(filename):
    response = send_from_directory('../../WebGLBuilds', filename)
    if filename.endswith('.br'):
        response.headers['Content-Encoding'] = 'br'
    elif filename.endswith('.gz'):
        response.headers['Content-Encoding'] = 'gzip'
    return response

# Serve favicon.ico from the specific directory
@app.route('/favicon.ico')
def serve_favicon():
    return send_from_directory(os.path.join('../../WebGLBuilds', 'TemplateData'), 'favicon.ico')

# Serve static files from 'static_files'
@app.route('/static/<path:filename>')
def serve_static_files(filename):
    return send_from_directory('../static_files', filename)

@app.route('/leaderboard')
def serve_leaderboard():
    backend_url_all_time = 'http://backend-service:10000/api/leaderboard-all-time'
    backend_url_24h = 'http://backend-service:10000/api/leaderboard-24h'
    
    try:
        leaderboard_response_all_time = requests.get(backend_url_all_time)
        leaderboard_data_all_time = leaderboard_response_all_time.json()
        
        leaderboard_response_24h = requests.get(backend_url_24h)
        leaderboard_data_24h = leaderboard_response_24h.json()
        
        return render_template('leaderboard.html', all_time_leaderboard=leaderboard_data_all_time, leaderboard_data_24h=leaderboard_data_24h)
    except requests.exceptions.RequestException as e:
        return str(e), 500

@app.route('/pl-guide') 
def serve_pl_guide():
    return render_template('pl-guide.html')

@app.route('/per-stats')
def serve_per_stats():
    backend_url = 'http://backend-service:10000/api/get-graph-data'
    response = requests.get(backend_url)
    data = response.json()
    return render_template('per-stats.html', chart_data=data)

# Route to serve the game
@app.route('/play')
def serve_game():
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def proxy_chat():
    backend_url = 'http://backend-service:10000/api/chat'
    response = requests.post(backend_url, json=request.json)
    return (response.content, response.status_code, response.headers.items())

@app.route('/save_playerdata', methods=['POST'])
def proxy_save_playerdata():
    backend_url = 'http://backend-service:10000/save_playerdata'  # Change to the correct URL and port of your backend server
    try:
        # Forward the request to the backend server
        response = requests.post(backend_url, json=request.get_json())
        return jsonify(response.json()), response.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/delete-score', methods=['POST'])
def proxy_delete_score():
    data = request.json
    score_to_delete = data.get('score')
    
    if not score_to_delete:
        return jsonify({"error": "No score provided"}), 400
    
    backend_url = 'http://backend-service:10000/api/delete-score'  # Replace with your backend URL

    # Forward the request to the backend
    response = requests.post(backend_url, json={'score': score_to_delete})

    # Return the backend response to the frontend
    return make_response(response.content, response.status_code)

port = int(os.environ.get('PORT', 5000))
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=port, ssl_context=context)
