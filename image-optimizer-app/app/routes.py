from flask import render_template
from flask import current_app as app
from flask import request
from flask import jsonify
from flask import send_file
import cv2
import os

# app = create_app()


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
    image = cv2.imread(imagePath)
    # Reduce the quality of the image by changing the compression level

    processedImagePath = os.path.join(
        app.config["UPLOAD_FOLDER"],
        "processed_" + str(int(os.path.getmtime(imagePath))) + "_" + file.filename,
    )
    print(f"Processed image path: {processedImagePath}")
    cv2.imwrite(processedImagePath, image, [int(cv2.IMWRITE_JPEG_QUALITY), quality])

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
