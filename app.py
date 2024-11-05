from flask import Flask, request, send_file, jsonify
from PIL import Image
import os
import io

app = Flask(__name__)

@app.route('/')
def index():
    return send_file('index.html')  # Serve the HTML file

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded.'}), 400

    file = request.files['file']
    target_size_kb = int(request.form.get('targetSize', 0))

    if file and file.filename != '':
        image = Image.open(file.stream)
        
        # Start with original quality
        quality = 85
        
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format='JPEG', quality=quality)
        img_byte_arr.seek(0)

        # Check the size of the compressed image
        while img_byte_arr.tell() > target_size_kb * 1024 and quality > 10:  # 10 is a minimum quality threshold
            quality -= 5  # Decrease quality to compress further
            img_byte_arr = io.BytesIO()  # Reset the byte array
            image.save(img_byte_arr, format='JPEG', quality=quality)
            img_byte_arr.seek(0)

        # After compression, check the size
        if img_byte_arr.tell() <= target_size_kb * 1024:
            img_byte_arr.seek(0)  # Seek to the start of the byte stream
            return send_file(img_byte_arr, mimetype='image/jpeg', as_attachment=True, download_name='compressed_image.jpg')
        else:
            return jsonify({'error': 'Unable to compress image to the desired size.'}), 400

    return jsonify({'error': 'Invalid file.'}), 400

if __name__ == '__main__':
    app.run(debug=True)
