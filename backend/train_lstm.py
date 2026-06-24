"""
train_lstm.py - End-to-end fine-tuning ResNeXt layer4 + LSTM
"""

import os, cv2, torch, random
import torch.nn as nn
import torchvision.models as models
import torchvision.transforms as transforms
from PIL import Image
from torch.utils.data import Dataset, DataLoader
from sklearn.model_selection import train_test_split

# ── Config ────────────────────────────────────────────
FAKE_DIR   = r"D:\ffpp_fake"
REAL_DIR   = r"D:\ffpp_real"
SAVE_PATH  = "lstm_classifier.pth"

MAX_FRAMES = 10
FRAME_STEP = 20
BATCH_SIZE = 8
LR_LSTM = 5e-6
LR_CNN  = 1e-8
EPOCHS  = 20
HIDDEN_DIM = 256
NUM_LAYERS = 2
# ─────────────────────────────────────────────────────

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Device: {DEVICE}")

face_cascade = cv2.CascadeClassifier(
    r"D:\Deepfake_project\haarcascade_frontalface_default.xml"
)

TRANSFORM = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406],
                         [0.229, 0.224, 0.225]),
])

class ResNeXtFeatureExtractor(nn.Module):
    def __init__(self):
        super().__init__()
        base = models.resnext50_32x4d(weights="IMAGENET1K_V1")
        base.fc = nn.Identity()
        for p in base.parameters():
            p.requires_grad = False
        for p in base.layer4.parameters():
            p.requires_grad = True
        self.model = base

    def forward(self, x):
        return self.model(x)

class LSTMClassifier(nn.Module):
    def __init__(self):
        super().__init__()
        self.lstm = nn.LSTM(2048, HIDDEN_DIM, NUM_LAYERS,
                            batch_first=True, dropout=0.3)
        self.fc   = nn.Linear(HIDDEN_DIM, 2)

    def forward(self, x):
        out, _ = self.lstm(x)
        return self.fc(out[:, -1, :])

def extract_face_frames(video_path):
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

class VideoDataset(Dataset):
    def __init__(self, samples):
        self.samples = samples

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        path, label = self.samples[idx]
        frames = extract_face_frames(path)

        if len(frames) < 2:
            # Return blank frames if video unreadable
            tensors = torch.zeros(MAX_FRAMES, 3, 224, 224)
            return tensors, torch.tensor(label, dtype=torch.long)

        tensors = torch.stack(
            [TRANSFORM(Image.fromarray(f)) for f in frames[:MAX_FRAMES]]
        )

        # Pad if fewer than MAX_FRAMES
        if tensors.shape[0] < MAX_FRAMES:
            pad     = torch.zeros(MAX_FRAMES - tensors.shape[0], 3, 224, 224)
            tensors = torch.cat([tensors, pad], dim=0)

        return tensors, torch.tensor(label, dtype=torch.long)

print("Collecting video paths...")
all_samples = []
for label, folder in [(1, FAKE_DIR), (0, REAL_DIR)]:
    videos = [f for f in os.listdir(folder)
              if f.lower().endswith((".mp4", ".avi", ".mov"))]
    print(f"  {'FAKE' if label else 'REAL'}: {len(videos)} videos")
    for fname in videos:
        all_samples.append((os.path.join(folder, fname), label))

random.shuffle(all_samples)
labels = [s[1] for s in all_samples]
tr_s, te_s = train_test_split(all_samples, test_size=0.3,
                               stratify=labels, random_state=42)
print(f"  Train: {len(tr_s)}  |  Test: {len(te_s)}\n")

train_loader = DataLoader(VideoDataset(tr_s), batch_size=BATCH_SIZE,
                          shuffle=True,  num_workers=0)
test_loader  = DataLoader(VideoDataset(te_s), batch_size=BATCH_SIZE,
                          shuffle=False, num_workers=0)

resnext   = ResNeXtFeatureExtractor().to(DEVICE)
lstm      = LSTMClassifier().to(DEVICE)
# Add after creating resnext and lstm models
# Load previous checkpoint if exists
if os.path.exists(SAVE_PATH):
    print("Loading previous checkpoint...")
    checkpoint = torch.load(SAVE_PATH, map_location=DEVICE)
    resnext.load_state_dict(checkpoint["resnext"])
    lstm.load_state_dict(checkpoint["lstm"])
    print("Checkpoint loaded!")
criterion = nn.CrossEntropyLoss()

optimizer = torch.optim.Adam([
    {"params": lstm.parameters(),                 "lr": LR_LSTM},
    {"params": resnext.model.layer4.parameters(), "lr": LR_CNN},
], weight_decay=1e-4)

scheduler = torch.optim.lr_scheduler.StepLR(optimizer, step_size=7, gamma=0.5)

print(f"{'='*55}")
print(f"  End-to-end Training | device={DEVICE} | epochs={EPOCHS}")
print(f"{'='*55}")
print(f"{'Epoch':>7} {'Loss':>8} {'Train%':>8} {'Val%':>8}")
print(f"{'─'*55}")

best_acc = 0.0

for epoch in range(1, EPOCHS + 1):

    resnext.train()
    lstm.train()
    loss_sum, correct, total = 0.0, 0, 0

    for frames, lbls in train_loader:
        frames = frames.to(DEVICE)
        lbls   = lbls.to(DEVICE)
        B, T, C, H, W = frames.shape

        optimizer.zero_grad()
        feats  = resnext(frames.view(B*T, C, H, W)).view(B, T, -1)
        logits = lstm(feats)
        loss   = criterion(logits, lbls)
        loss.backward()
        optimizer.step()

        loss_sum += loss.item()
        correct  += (logits.argmax(1) == lbls).sum().item()
        total    += lbls.size(0)

    train_acc = correct / total * 100

    resnext.eval()
    lstm.eval()
    vc, vt = 0, 0
    with torch.no_grad():
        for frames, lbls in test_loader:
            frames = frames.to(DEVICE)
            lbls   = lbls.to(DEVICE)
            B, T, C, H, W = frames.shape
            feats  = resnext(frames.view(B*T, C, H, W)).view(B, T, -1)
            vc    += (lstm(feats).argmax(1) == lbls).sum().item()
            vt    += lbls.size(0)

    val_acc = vc / vt * 100
    scheduler.step()

    saved = ""
    if val_acc > best_acc:
        best_acc = val_acc
        torch.save({
            "resnext": resnext.state_dict(),
            "lstm":    lstm.state_dict(),
        }, SAVE_PATH)
        saved = "  ✓"

    print(f"  {epoch:02d}/{EPOCHS}  "
          f"{loss_sum/len(train_loader):>8.4f}  "
          f"{train_acc:>7.1f}%  "
          f"{val_acc:>7.1f}%{saved}")

print(f"{'─'*55}")
print(f"\n  Best val accuracy : {best_acc:.1f}%")
print(f"  Saved → {SAVE_PATH}")
print(f"{'='*55}\n")