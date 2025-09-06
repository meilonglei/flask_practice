import os
from flask import Flask, request, jsonify, render_template, url_for, send_file
import cv2
from ultralytics import YOLO
import uuid
from flask import send_file

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')

# 🔑 设置 API 密钥
API_KEY = "your-secret-api-key-12345"

app.config['UPLOAD_FOLDER'] = 'yolo_app/static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

model = YOLO('yolov8s.pt')

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/api/detect', methods=['POST'])
def api_detect():
    # 🔒 验证密钥
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith("Bearer "):
        return jsonify({"error": "Missing Authorization header"}), 401
    
    token = auth_header.split(" ")[1]
    if token != API_KEY:
        return jsonify({"error": "Invalid API Key"}), 401

    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if file and allowed_file(file.filename):
        ext = file.filename.rsplit('.', 1)[1].lower()
        filename = f"{uuid.uuid4().hex}.{ext}"
        input_path = os.path.join(app.config['UPLOAD_FOLDER'], 'input_' + filename)
        output_path = os.path.join(app.config['UPLOAD_FOLDER'], 'output_' + filename)
        file.save(input_path)

        try:
            results = model(input_path)
            result = results[0]
            result.save(filename=output_path)

            detections = []
            for box in result.boxes:
                detections.append({
                    "class": result.names[int(box.cls)],
                    "confidence": float(box.conf),
                    "bbox": box.xyxy[0].tolist()
                })

            return jsonify({
                "success": True,
                "detections": detections,
                "image_url": url_for('static', filename=f'uploads/output_{filename}')
            })
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    return jsonify({"error": "File type not allowed"}), 400


@app.route('/static/uploads/<filename>')
def uploaded_file(filename):
    directory = app.config['UPLOAD_FOLDER']
    full_path = os.path.join(directory, filename)
    print(directory)
    print(filename)
    print(f"完整路径: {full_path}")
    print(f"绝对路径: {os.path.abspath(full_path)}")
    print(f"是否存在: {os.path.exists(full_path)}")
    print(f"是否是文件: {os.path.isfile(full_path)}")
    
    if not os.path.exists(full_path):
        return "File not found", 404
    
    return send_file(os.path.abspath(full_path))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)