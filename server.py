import os
import requests
from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from services.Claude import Claude
from werkzeug.utils import secure_filename
import base64
from datetime import datetime

load_dotenv()

app = Flask(__name__)
CORS(app)
HTTP_OK = 200
HTTP_BAD_REQUEST = 400

UPLOAD_FOLDER = 'static'

client = Claude(api_key = os.getenv('ANTHROPIC_API_KEY'))

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def home():
    return "WELCOME WHATSUP SIUUUUUU"


@app.route('/process-img', methods=['POST'])
def process_image():
    api_url = f'http://127.0.0.1:5000/get_image'
    response = requests.get(api_url)

    if response.status_code != 200:
        return jsonify({"error": "Failed to fetch image from API"}), 400
    
    # Get the image content and MIME type
    image_content = response.content
    mime_type = response.headers.get('Content-Type', 'image/jpeg')
    
    # Generate a unique filename
    current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = secure_filename(f"image_{current_time}.jpg")
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    
    # Save the image temporarily
    with open(filepath, 'wb') as f:
        f.write(image_content)
    
    try:
        # Encode the image to base64
        image_data = base64.b64encode(image_content).decode('utf-8')
        
        # Process the image with Claude
        response = client.image_to_text(image_data, mime_type, "claude-3-5-sonnet-20241022")
        description_text = response.content[0].text
        
        return jsonify({"description": description_text}), 200
    except Exception as e:
        # Clean up the temporary file in case of an error
        # if os.path.exists(filepath):
        #     os.remove(filepath)
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    app.run(port=8000,debug=True)