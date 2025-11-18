"""
Flask Backend API for Voice Analysis
Endpoints:
- POST /analyze - Analyze audio file
- GET /health - Health check
"""

import os
import sys

# Add FFmpeg to PATH before importing other modules
def setup_ffmpeg():
    """Find and add FFmpeg to PATH if not already available"""
    # Check if ffmpeg is already in PATH
    import subprocess
    try:
        subprocess.run(['ffmpeg', '-version'], capture_output=True, timeout=2)
        return  # FFmpeg already available
    except:
        pass
    
    # Search for local FFmpeg installation
    search_paths = [
        os.path.join(os.path.dirname(__file__), 'ffmpeg'),
        'C:\\ffmpeg\\bin',
    ]
    
    for base_path in search_paths:
        if os.path.exists(base_path):
            for root, dirs, files in os.walk(base_path):
                if 'ffmpeg.exe' in files:
                    ffmpeg_bin = root
                    current_path = os.environ.get('PATH', '')
                    if ffmpeg_bin not in current_path:
                        os.environ['PATH'] = ffmpeg_bin + os.pathsep + current_path
                        print(f"✓ FFmpeg found and added to PATH: {ffmpeg_bin}")
                    return
    
    print("⚠ WARNING: FFmpeg not found! Audio analysis may fail.")
    print("  Run: python setup_ffmpeg.py")

# Setup FFmpeg before importing libraries that need it
setup_ffmpeg()

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from voice_analyzer import VoiceAnalyzer
from werkzeug.utils import secure_filename

app = Flask(__name__, static_folder='../frontend', static_url_path='')
CORS(app, resources={
    r"/*": {
        "origins": "*",
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"],
        "expose_headers": ["Content-Type"],
        "supports_credentials": False
    }
})

# File Upload Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'wav', 'mp3', 'ogg', 'm4a', 'flac', 'webm'}

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# Initialize analyzer
print("Initializing Voice Analyzer...")
analyzer = VoiceAnalyzer()
print("Server ready!")

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """Serve the main index.html page"""
    return send_from_directory('../frontend', 'index.html')

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "Voice Analysis API",
        "version": "1.0"
    })

@app.route('/analyze', methods=['POST', 'OPTIONS'])
def analyze_audio():
    """Analyze uploaded audio file"""
    # Handle preflight OPTIONS request
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
        return response
    
    try:
        # Check if file is present
        if 'audio' not in request.files:
            return jsonify({"error": "No audio file provided"}), 400
        
        file = request.files['audio']
        
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        
        if not allowed_file(file.filename):
            return jsonify({"error": f"File type not allowed. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"}), 400
        
        # Save file
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        print(f"Analyzing file: {filename}")
        
        # Analyze audio
        result = analyzer.analyze(filepath)
        
        # Clean up
        os.remove(filepath)
        
        response_data = {
            "success": True,
            "data": result
        }
        print(f"Sending response: success={response_data['success']}, data keys={list(result.keys())}")
        
        response = jsonify(response_data)
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
        return response
    
    except Exception as e:
        print(f"Error: {str(e)}")
        response = jsonify({
            "success": False,
            "error": str(e)
        })
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
        return response, 500

@app.errorhandler(413)
def request_entity_too_large(error):
    return jsonify({"error": "File too large. Maximum size is 10MB"}), 413

if __name__ == '__main__':
    print("\n" + "="*50)
    print("Voice Analysis API Server")
    print("="*50)
    print("Server running on: http://localhost:5000")
    print("Endpoints:")
    print("  - GET  /health  - Health check")
    print("  - POST /analyze - Analyze audio")
    print("="*50 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
