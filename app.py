# pip install flask rembg pillow numpy

from flask import Flask, request, jsonify
# from flask_cors import CORS
import rembg
import numpy as np
from PIL import Image
import io
import base64

app = Flask(__name__)
# CORS(app)

def crop_image(image):
    if image.mode != 'RGBA':
        image = image.convert('RGBA')
    r, g, b, a = image.split()
    bbox = a.getbbox()
    if bbox:
        return image.crop(bbox)
    else:
        return image

def process_image(image_file, crop):
    input_image = Image.open(image_file)
    input_array = np.array(input_image)
    output_array = rembg.remove(input_array)
    output_image = Image.fromarray(output_array)
    
    if crop:
        output_image = crop_image(output_image)

    buffered = io.BytesIO()
    output_image.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")

    return img_str

@app.route('/process', methods=['POST'])
def process():
    try:
        crop = request.form.get('crop', default=0, type=int)
        if 'image' not in request.files:
            return jsonify({"status": "error", "message": "No file part"}), 400

        image_file = request.files['image']
        if image_file.filename == '':
            return jsonify({"status": "error", "message": "No selected file"}), 400

        img_str = process_image(image_file, crop)
        return jsonify({"status": "success", "image": img_str})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
