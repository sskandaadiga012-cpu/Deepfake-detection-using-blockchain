"""
extract_video_features.py
Extracts ResNeXt features from actual .mp4 videos.
Uses all Train + Test videos for maximum data.
Place in D:\Deepfake_project\ and run once.
"""

import os, cv2, torch
import torch.nn as nn
import torchvision.models as models
import torchvision.transforms as transforms
from PIL import Image

# All 4 folders combined
DIRS = [
    (1, r"D:\Deepfake_project\dataset\Train\fake"),
    (0, r"D:\Deepfake_project\dataset\Train\real"),
    (1, r"D:\Deepfake_project\dataset\Test\fake"),
    (0, r"D:\Deepfake_project\dataset\Test\real"),
]

SAVE_FEAT  = r"D:\Deepfake_project\video_features.pt"
SAVE_LABEL = r"D:\Deepfake_project\video_labels.pt"
NUM_FRAMES = 20

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Device: {DEVICE}")

TRANSFORM = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406],
                         [0.229, 0.224, 0.225]),
])

# Frozen ResNeXt
print("Loading ResNeXt...")
resnext = models.resnext50_32x4d(
    weights=models.ResNeXt50_32X4D_Weights.DEFAULT)
resnext.fc = nn.Identity()
resnext.eval().to(DEVICE)
for p in resnext.parameters():
    p.requires_grad = False

def extract_frames(path):
    cap   = cv2.VideoCapture(path)
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    if total < 2:
        cap.release()
        return []
    step   = max(1, total // NUM_FRAMES)
    frames = []
    for i in range(0, total, step):
        cap.set(cv2.CAP_PROP_POS_FRAMES, i)
        ret, frame = cap.read()
        if not ret:
            break
        frames.append(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        if len(frames) >= NUM_FRAMES:
            break
    cap.release()
    return frames

all_features = []
all_labels   = []
skipped      = 0

for label, folder in DIRS:
    tag    = "FAKE" if label else "REAL"
    videos = [f for f in os.listdir(folder)
              if f.lower().endswith((".mp4", ".avi", ".mov", ".mkv"))]
    print(f"\n{tag} ({folder.split(chr(92))[-2]}): {len(videos)} videos")

    for i, fname in enumerate(videos):
        frames = extract_frames(os.path.join(folder, fname))
        if len(frames) < 2:
            skipped += 1
            continue

        tensors = torch.stack(
            [TRANSFORM(Image.fromarray(f)) for f in frames]
        ).to(DEVICE)

        with torch.no_grad():
            feats = resnext(tensors)   # (T, 2048)

        all_features.append(feats.cpu())
        all_labels.append(label)

        if (i + 1) % 100 == 0:
            print(f"  {i+1}/{len(videos)} done...")

print(f"\nSkipped : {skipped}")
print(f"Total   : {len(all_features)} videos")

# Pad sequences
max_len = max(f.shape[0] for f in all_features)
padded  = torch.zeros(len(all_features), max_len, 2048)
for i, f in enumerate(all_features):
    padded[i, :f.shape[0]] = f

labels = torch.tensor(all_labels, dtype=torch.long)

torch.save(padded, SAVE_FEAT)
torch.save(labels, SAVE_LABEL)

print(f"\nSaved video_features.pt : {padded.shape}")
print(f"Fake: {(labels==1).sum().item()}  Real: {(labels==0).sum().item()}")
print("Done!")