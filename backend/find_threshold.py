"""
find_threshold.py - Step 3
Finds optimal detection threshold on test set.
Run after train_lstm.py
"""

import torch
import torch.nn as nn
from sklearn.model_selection import train_test_split

FEATURES_PATH = r"D:\Deepfake_project\video_features.pt"
LABELS_PATH   = r"D:\Deepfake_project\video_labels.pt"
HIDDEN_DIM    = 256
NUM_LAYERS    = 2

class LSTMClassifier(nn.Module):
    def __init__(self):
        super().__init__()
        self.lstm = nn.LSTM(2048, HIDDEN_DIM, NUM_LAYERS,
                            batch_first=True, dropout=0.3)
        self.fc   = nn.Linear(HIDDEN_DIM, 2)
    def forward(self, x):
        out, _ = self.lstm(x)
        return self.fc(out[:, -1, :])

X = torch.load(FEATURES_PATH)
y = torch.load(LABELS_PATH)

_, te_idx = train_test_split(list(range(len(X))), test_size=0.3,
                              stratify=y.tolist(), random_state=42)
X_test = X[te_idx]
y_test = y[te_idx]

lstm = LSTMClassifier()
lstm.load_state_dict(torch.load("lstm_classifier.pth", map_location="cpu"))
lstm.eval()

all_probs, all_labels = [], []
with torch.no_grad():
    for i in range(0, len(X_test), 4):
        feats = X_test[i:i+4]
        lbls  = y_test[i:i+4]
        probs = torch.softmax(lstm(feats), dim=1)[:,1]
        all_probs.extend(probs.tolist())
        all_labels.extend(lbls.tolist())

print(f"Test samples : {len(all_labels)}")
print(f"Avg prob_fake: {sum(all_probs)/len(all_probs):.4f}\n")

best_thresh = 0.5
best_acc    = 0.0

for thresh in [0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]:
    correct = sum(1 for p,l in zip(all_probs, all_labels)
                  if (p > thresh) == bool(l))
    acc = correct / len(all_labels) * 100
    marker = ""
    if acc > best_acc:
        best_acc    = acc
        best_thresh = thresh
        marker      = "  ← best"
    print(f"Threshold {thresh:.1f}: {acc:.1f}%{marker}")

print(f"\nBest threshold: {best_thresh}  ({best_acc:.1f}%)")
print(f"\nUpdate app.py: is_fake = prob_fake > {best_thresh}")