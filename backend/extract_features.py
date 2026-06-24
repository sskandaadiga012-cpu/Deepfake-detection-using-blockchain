"""
extract_features.py
Extracts features exactly matching the training pipeline:
  1. Every 20th frame, max 10 frames (matches extract_frames.py)
  2. Face crop with scaleFactor=1.3, minNeighbors=5 (matches faces_extract.py)
  3. Resize to 224x224
  4. ResNeXt features
"""

import os, cv2, torch
import torch.nn as nn
import torchvision.models as models
import torchvision.transforms as transforms
from PIL import Image

FAKE_DIR   = r"D:\ffpp_fake"
REAL_DIR   = r"D:\ffpp_real"
SAVE_FEAT  = r"D:\Deepfake_project\video_features.pt"
SAVE_LABEL = r"D:\Deepfake_project\video_labels.pt"

MAX_FRAMES  = 10   # matches extract_frames.py
FRAME_STEP  = 20   # every 20th frame

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Device: {DEVICE}")

face_cascade = cv2.CascadeClassifier(
    r"D:\Deepfake_project\haarcascade_frontalface_default.xml"
)

print("Loading ResNeXt...")
resnext = models.resnext50_32x4d(weights="IMAGENET1K_V1")
resnext = torch.nn.Sequential(*list(resnext.children())[:-1])
resnext.eval().to(DEVICE)
for p in resnext.parameters():
    p.requires_grad = False

TRANSFORM = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406],
                         std=[0.229, 0.224, 0.225]),
])

def extract_face_frames(video_path):
    """Exactly matches extract_frames.py + faces_extract.py pipeline."""
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
            # Face detection (matches faces_extract.py)
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
                break  # only first face

        frame_count += 1

    cap.release()
    return faces_list

all_features = []
all_labels   = []
skipped      = 0

for label, folder in [(1, FAKE_DIR), (0, REAL_DIR)]:
    tag    = "FAKE" if label else "REAL"
    videos = [f for f in os.listdir(folder)
              if f.lower().endswith((".mp4", ".avi", ".mov"))]
    print(f"\n{tag}: {len(videos)} videos")

    for i, fname in enumerate(videos):
        frames = extract_face_frames(os.path.join(folder, fname))
        if len(frames) < 2:
            skipped += 1
            continue

        tensors = torch.stack(
            [TRANSFORM(Image.fromarray(f)) for f in frames]
        ).to(DEVICE)

        with torch.no_grad():
            feats = resnext(tensors)
            feats = feats.view(feats.size(0), -1)  # (T, 2048)

        all_features.append(feats.cpu())
        all_labels.append(label)

        if (i + 1) % 100 == 0:
            print(f"  {i+1}/{len(videos)} done...")

print(f"\nSkipped : {skipped}")
print(f"Total   : {len(all_features)} videos")

max_len = max(f.shape[0] for f in all_features)
padded  = torch.zeros(len(all_features), max_len, 2048)
for i, f in enumerate(all_features):
    padded[i, :f.shape[0]] = f

labels = torch.tensor(all_labels, dtype=torch.long)
torch.save(padded, SAVE_FEAT)
torch.save(labels, SAVE_LABEL)

print(f"\nSaved: {padded.shape}")
print(f"Fake: {(labels==1).sum().item()}  Real: {(labels==0).sum().item()}")
print("Done! Now run train_lstm.py")