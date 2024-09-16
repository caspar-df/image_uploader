import os
from flask import Flask, request, redirect, url_for, render_template, flash, send_from_directory
from werkzeug.utils import secure_filename
from PIL import Image

# Configuration
UPLOAD_FOLDER = 'uploads/'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SECRET_KEY'] = 'supersecretkey'  # Needed for flash messages

# Ensure the upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # Check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # If the user does not select a file, the browser submits an empty file without a filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
        
            try:
                with Image.open(filepath) as img:
                    rotated_img = img.rotate(90)  # Rotate 90 degrees clockwise
                    rotated_filename = 'rotated_' + filename
                    rotated_filepath = os.path.join(app.config['UPLOAD_FOLDER'], 'rotated_' + filename)
                    rotated_img.save(rotated_filepath)
                    flash('File successfully uploaded and rotated', 'success')
                    return redirect(url_for('uploaded_file', filename='rotated_' + filename))
            except Exception as e:
                flash(f'Failed to rotate image: {e}', 'error')
                return redirect(url_for('uploaded_file', filename=rotated_filename))
            
    return render_template('upload.html')

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return render_template('uploaded.html', filename=filename)

@app.route('/uploads/download/<filename>')
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
