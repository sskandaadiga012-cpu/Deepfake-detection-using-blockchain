"""
model.py - Model architectures matching training pipeline exactly.
ResNeXt uses same structure as feature_extraction.py
"""

import torch
import torch.nn as nn
import torchvision.models as models


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
    """2-layer LSTM classifier."""
    def __init__(self):
        super().__init__()
        self.lstm = nn.LSTM(2048, 256, 2,
                            batch_first=True, dropout=0.3)
        self.fc   = nn.Linear(256, 2)

    def forward(self, x):
        out, _ = self.lstm(x)
        return self.fc(out[:, -1, :])