from flask import render_template
from flask import current_app as app
from flask import request
from flask import jsonify
import cv2
import os

# app = create_app()

@app.route('/')
def home():
    print('we got here')
    return render_template('base.html')

# add route to upload image
@app.route('/upload', methods=['POST']) 
def upload():
    if 'image' not in request.files:
        return jsonify({'error': 'No image file provided'}), 400

    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    # Save the image to local storage
    imagePath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(imagePath)

    # Process the image with OpenCV
    image = cv2.imread(imagePath)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    processedImagePath = os.path.join(app.config['UPLOAD_FOLDER'], 'processed_' + file.filename)
    cv2.imwrite(processedImagePath, gray)

    # Return success response
    return jsonify({'message': 'Image processed successfully', 'processed_image': processedImagePath}, 200)


# add route to see all registered routes
@app.route('/routes')
def routes():
    routes = []
    for rule in app.url_map.iter_rules():
        routes.append(f"{rule.endpoint} - {rule.rule}")
    return  "<br>".join(routes)
