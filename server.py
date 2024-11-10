import os
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from services.Claude import Claude
from werkzeug.utils import secure_filename
from datetime import datetime
from PIL import Image

load_dotenv()

app = Flask(__name__)
CORS(app, origins=["http://localhost:5173"])
HTTP_OK = 200
HTTP_BAD_REQUEST = 400

UPLOAD_FOLDER = 'static'

client = Claude(api_key = os.getenv('ANTHROPIC_API_KEY'))

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def home():
    return "WELCOME WHATSUP SIUUUUUU"


@app.route('/help', methods=['POST'])
def help():
    #PROCESS USER PROMPT
    print(f"Received new request with body {request.data}")
    data = request.json
    text = data.get('text','')
    user_prompt = str(text)
    
    print("Taking a screenshot from current feed")
    #GET PICTURE
    api_url = f'http://127.0.0.1:5000/screenshot'
    response = requests.get(api_url)

    if response.status_code != 200:
        return jsonify({"error": "Failed to fetch image from API"}), 400
    
    print("Processing image got from screenshot")
    # Get the image content and MIME type
    image_content = response.content
    mime_type = response.headers.get('Content-Type', 'image/png')
    
    # Generate a unique filename
    current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = secure_filename(f"image_{current_time}.png")
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    
    # Save the image temporarily
    with open(filepath, 'wb') as f:
        f.write(image_content)

    try:
        # Encode the image to base64
        # image_data = base64.b64encode(image_content).decode('utf-8')
        print("Attempting analysis with Anthropic")
        # Process the image with Claude
        response = client.image_to_text(filepath, mime_type, "claude-3-5-sonnet-20241022")
        #IMAGE DETAILS
        description_text = response.content[0].text
        print(description_text)
        return jsonify(description_text), 200
    except Exception as e:
        return jsonify({"error": str(e)}), HTTP_BAD_REQUEST

if __name__ == '__main__':
    app.run(port=8000,debug=True)