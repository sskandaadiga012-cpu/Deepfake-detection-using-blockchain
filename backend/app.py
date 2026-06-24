"""
app.py - Deepfake Detection API
Inference matches training pipeline exactly.
"""

from flask import Flask, request, jsonify
from flask_cors import CORS                    
from blockchain import log_result, get_result, compute_hash
from model import ResNeXtFeatureExtractor, LSTMClassifier
import torch
import torchvision.transforms as transforms
from PIL import Image
import cv2, tempfile, os

app = Flask(__name__)
CORS(app)
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024

# Face detector
face_cascade = cv2.CascadeClassifier(
    r"D:\Deepfake_project\haarcascade_frontalface_default.xml"
)

# Load models
print("Loading models...")
checkpoint = torch.load("lstm_classifier.pth", map_location="cpu")
resnext = ResNeXtFeatureExtractor()
lstm    = LSTMClassifier()
resnext.load_state_dict(checkpoint["resnext"])
lstm.load_state_dict(checkpoint["lstm"])
resnext.eval()
lstm.eval()
print("Models loaded!")

# Same transform as feature_extraction.py (no normalize — matches training)
TRANSFORM = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406],
                         std=[0.229, 0.224, 0.225]),
])
MAX_FRAMES  = 10
FRAME_STEP  = 20
THRESHOLD   = 0.5  # update after find_threshold.py

def extract_face_frames(video_path):
    """Exactly matches extract_frames.py + faces_extract.py"""
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return []

    frame_count = 0
    saved_count = 0
    faces_list  = []

    while True:
        ret, frame = cap.read()
        if not ret or saved_count >= MAX_FRAMES:
            break

        if frame_count % FRAME_STEP == 0:
            gray  = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.3, 5)

            for (x, y, w, h) in faces:
                face = frame[y:y+h, x:x+w]
                if face.size == 0:
                    continue
                face = cv2.resize(face, (224, 224))
                face = cv2.cvtColor(face, cv2.COLOR_BGR2RGB)
                faces_list.append(face)
                saved_count += 1
                break

        frame_count += 1

    cap.release()
    return faces_list

def run_detection(video_path):
    frames = extract_face_frames(video_path)

    if not frames:
        return {"result": "Error", "confidence": 0, "features": b""}

    tensors = torch.stack(
        [TRANSFORM(Image.fromarray(f)) for f in frames]
    )

    with torch.no_grad():
        features     = resnext(tensors)
        features_seq = features.unsqueeze(0)
        logits       = lstm(features_seq)
        probs        = torch.softmax(logits, dim=1)[0]

    prob_fake  = probs[1].item()
    is_fake    = prob_fake > THRESHOLD
    confidence = int(prob_fake * 100 if is_fake else (1 - prob_fake) * 100)
    result     = "Deepfake" if is_fake else "Real"

    return {
        "result":     result,
        "confidence": confidence,
        "features":   features.numpy().tobytes(),
    }

@app.route("/upload", methods=["POST"])
def upload_video():
    if "video" not in request.files:
        return jsonify({"error": "No video file provided"}), 400

    video_file = request.files["video"]
    device_id  = request.form.get("device", "unknown-device")

    if video_file.filename == "":
        return jsonify({"error": "Empty filename"}), 400

    suffix = os.path.splitext(video_file.filename)[1] or ".mp4"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        video_file.save(tmp.name)
        tmp_path = tmp.name

    try:
        detection = run_detection(tmp_path)

        if detection["result"] == "Error":
            return jsonify({"error": "Could not extract frames"}), 422

        metadata   = f"deviceID:{device_id};score:{detection['confidence']/100:.2f}"
        tx_id      = log_result(detection["features"], metadata, detection["result"])
        video_hash = compute_hash(str(detection["features"]) + metadata)

        return jsonify({
            "result":     detection["result"],
            "confidence": f"{detection['confidence']}%",
            "tx_id":      tx_id,
            "video_hash": video_hash,
            "device":     device_id,
        })
    finally:
        os.unlink(tmp_path)

@app.route("/verify", methods=["GET"])
def verify_video():
    video_hash = request.args.get("hash", "")
    if not video_hash:
        return jsonify({"error": "Provide ?hash=<video_hash>"}), 400
    try:
        return jsonify(get_result(video_hash))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/health", methods=["GET"])
def health():
    from web3 import Web3
    w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
    return jsonify({
        "flask":      "ok",
        "blockchain": "connected" if w3.is_connected() else "disconnected",
        "block":      w3.eth.block_number if w3.is_connected() else None,
    })

if __name__ == "__main__":
    print("Starting Deepfake Detection API...")
    print("  POST http://localhost:5000/upload")
    print("  GET  http://localhost:5000/verify?hash=<hash>")
    print("  GET  http://localhost:5000/health")
    app.run(debug=True, host="0.0.0.0", port=5000)