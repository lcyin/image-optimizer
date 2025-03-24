from flask import render_template
from flask import current_app as app
from flask import request
from flask import jsonify
from flask import send_file
import cv2
import os
import imghdr
from PIL import Image

# app = create_app()


def is_valid_image(file):
    """Validate the uploaded file is a valid image."""
    # Check MIME type
    if not file.content_type.startswith("image/"):
        return False, "Uploaded file is not an image"

    # Validate file extension
    allowed_extensions = {"jpg", "jpeg", "png", "gif"}
    if not (
        "." in file.filename
        and file.filename.rsplit(".", 1)[1].lower() in allowed_extensions
    ):
        return False, "Unsupported file extension"

    # Validate file content using imghdr
    file_content = file.read()
    file.seek(0)  # Reset the file pointer after reading
    if imghdr.what(None, h=file_content) not in allowed_extensions:
        return False, "File content does not match an image type"

    # Validate file content using Pillow
    try:
        Image.open(file).verify()
    except Exception:
        return False, "File content is not a valid image"

    return True, None


def is_valid_processed_image(path):
    """Validate the processed image exists and is valid."""
    if not os.path.exists(path):
        return False, "Processed image does not exist"
    try:
        with Image.open(path) as img:
            img.verify()
    except Exception:
        return False, "Processed image is not valid"
    return True, None


@app.route("/")
def home():
    print("we got here")
    return render_template("base.html")


# add route to upload image
@app.route("/upload", methods=["POST"])
def upload():
    if "image" not in request.files:
        return jsonify({"error": "No image file provided"}), 400

    file = request.files["image"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    # Validate the uploaded file
    is_valid, error_message = is_valid_image(file)
    if not is_valid:
        return jsonify({"error": error_message}), 400

    # Ensure the upload folder exists
    if not os.path.exists(app.config["UPLOAD_FOLDER"]):
        os.makedirs(app.config["UPLOAD_FOLDER"])

    # Get the quality parameter from the request, default to 10 if not provided
    quality = request.form.get("quality", default=10, type=int)
    print(f"Quality parameter received: {quality}")

    # Save the image to local storage
    imagePath = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
    file.save(imagePath)

    # Process the image with OpenCV
    imageCv = cv2.imread(imagePath)
    # Reduce the quality of the image by changing the compression level

    processedImagePath = os.path.join(
        app.config["UPLOAD_FOLDER"],
        "processed_" + str(int(os.path.getmtime(imagePath))) + "_" + file.filename,
    )
    print(f"Processed image path: {processedImagePath}")
    cv2.imwrite(processedImagePath, imageCv, [int(cv2.IMWRITE_JPEG_QUALITY), quality])

    # Validate the processed image
    is_valid, error_message = is_valid_processed_image(processedImagePath)
    if not is_valid:
        return jsonify({"error": error_message}), 500

    # Return success response with the compressed image
    return send_file(
        processedImagePath,
        mimetype="image/jpeg",
        as_attachment=True,
        download_name=f"compressed_{file.filename}",
    )


# add route to see all registered routes
@app.route("/routes")
def routes():
    routes = []
    for rule in app.url_map.iter_rules():
        routes.append(f"{rule.endpoint} - {rule.rule}")
    return "<br>".join(routes)
