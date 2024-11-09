import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from services.Claude import Claude
from werkzeug.utils import secure_filename
import base64

load_dotenv()

app = Flask(__name__)
CORS(app)
HTTP_OK = 200
HTTP_BAD_REQUEST = 400

UPLOAD_FOLDER = 'static'
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png'}

client = Claude(api_key = os.getenv('ANTHROPIC_API_KEY'))

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def home():
    return "WELCOME WHATSUP SIUUUUUU"

@app.route('/test-claude', methods=['POST'])
def process_image():
    if 'file' not in request.files:
        return "CANT FIND SHIT", HTTP_BAD_REQUEST
    file = request.files['file']
    if file.filename == '':
        return "No selected file", HTTP_BAD_REQUEST
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        try:
            with open(filepath, 'rb') as image_file:
                image_data = base64.b64encode(image_file.read()).decode('utf-8')
            response = client.image_to_text(image_data,"image/jpeg","claude-3-5-sonnet-20241022")
            description_text = response.content[0].text
            return jsonify({"description": description_text}), HTTP_OK
        except Exception as e:
            return jsonify({"error": str(e)}), HTTP_BAD_REQUEST 
        # finally:
        #     os.remove(filepath)

if __name__ == '__main__':
    app.run(debug=True)