from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import traceback
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))  # Ensure local imports work
from watch_pharmacy_data import process_file  # Import `process_file` directly

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes (allows frontend requests)

# Directory to store uploaded files
UPLOAD_FOLDER = "pharmacy_data"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # Ensure folder exists
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

@app.route("/upload", methods=["POST"])
def upload_file():
    """Handles file uploads and processes them immediately."""
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    # Save the file
    file_path = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
    file.save(file_path)

    print(f"✅ File received: {file.filename}")
    print(f"📂 File saved in {UPLOAD_FOLDER}. Now processing...")

    # Directly call `process_file()` to process the uploaded file
    try:
        process_file(file_path)  # File is processed immediately
        print(f"✅ Successfully processed {file.filename} and sent to Rails")
        return jsonify({"message": f"File '{file.filename}' uploaded and processed successfully."}), 200
    except Exception as e:
        print(f"❌ Error processing {file.filename}: {e}")
        traceback.print_exc()
        return jsonify({"error": f"Failed to process file: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
