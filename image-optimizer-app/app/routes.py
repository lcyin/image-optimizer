from flask import render_template
from flask import current_app as app
from flask import request
from flask import jsonify
from flask import send_file
import cv2
import os
import imghdr
from PIL import Image
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
        file.seek(0)  # Reset the file pointer after reading
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
    try:
        if "image" not in request.files:
            logger.error("No image file provided in the request")
            return jsonify({"error": "No image file provided"}), 400

        file = request.files["image"]
        if file.filename == "":
            logger.error("No file selected for upload")
            return jsonify({"error": "No selected file"}), 400

        # Validate the uploaded file
        is_valid, error_message = is_valid_image(file)
        if not is_valid:
            logger.error(f"Image validation failed: {error_message}")
            return jsonify({"error": error_message}), 400

        # Ensure the upload folder exists
        if not os.path.exists(app.config["UPLOAD_FOLDER"]):
            try:
                os.makedirs(app.config["UPLOAD_FOLDER"])
                logger.info(f"Created upload folder: {app.config['UPLOAD_FOLDER']}")
            except Exception as e:
                logger.exception("Failed to create upload folder")
                return jsonify({"error": "Failed to create upload folder"}), 500

        # Get the quality parameter from the request
        try:
            quality = request.form.get("quality", default=10, type=int)
            if not (0 <= quality <= 100):
                logger.error(f"Invalid quality value: {quality}")
                return jsonify({"error": "Quality must be between 0 and 100"}), 400
            logger.info(f"Quality parameter received: {quality}")
        except Exception as e:
            logger.exception("Failed to parse quality parameter")
            return jsonify({"error": "Invalid quality parameter"}), 400

        # Save the image to local storage
        try:
            imagePath = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
            file.save(imagePath)
            logger.info(f"Image saved to: {imagePath}")
        except Exception as e:
            logger.exception("Failed to save the uploaded image")
            return jsonify({"error": "Failed to save the uploaded image"}), 500

        # Process the image
        processedImagePath = os.path.join(
            app.config["UPLOAD_FOLDER"],
            "processed_" + str(int(os.path.getmtime(imagePath))) + "_" + file.filename,
        )

        if file.filename.lower().endswith(".gif"):
            # Handle GIF files using Pillow
            logger.info(f"Processing GIF image: {imagePath}")
            try:
                with Image.open(imagePath) as img:
                    img.save(processedImagePath, format="GIF", optimize=True)
            except Exception as e:
                logger.exception("Failed to process GIF image")
                return jsonify({"error": "Failed to process GIF image"}), 500
        else:
            # Handle other image formats using OpenCV
            logger.info(f"Processing image, output path: {processedImagePath}")
            imageCv = cv2.imread(imagePath)
            if imageCv is None:
                logger.error(f"Failed to read image: {imagePath}")
                return jsonify({"error": "Failed to process the uploaded image"}), 400

            success = cv2.imwrite(
                processedImagePath, imageCv, [int(cv2.IMWRITE_JPEG_QUALITY), quality]
            )
            if not success:
                logger.error(f"Failed to write processed image: {processedImagePath}")
                return jsonify({"error": "Failed to save the processed image"}), 500

        # Validate the processed image
        is_valid, error_message = is_valid_processed_image(processedImagePath)
        if not is_valid:
            logger.error(f"Processed image validation failed: {error_message}")
            return jsonify({"error": error_message}), 500

        # Return success response with the compressed image
        logger.info(f"Image processed successfully: {processedImagePath}")
        return send_file(
            processedImagePath,
            mimetype=(
                "image/gif" if file.filename.lower().endswith(".gif") else "image/jpeg"
            ),
            as_attachment=True,
            download_name=f"compressed_{file.filename}",
        )
    except Exception as e:
        logger.exception("An unexpected error occurred during the upload process")
        return jsonify({"error": "An unexpected error occurred"}), 500


# add route to see all registered routes
@app.route("/routes")
def routes():
    routes = []
    for rule in app.url_map.iter_rules():
        routes.append(f"{rule.endpoint} - {rule.rule}")
    return "<br>".join(routes)
