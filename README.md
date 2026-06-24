# Deepfake Detection using Blockchain and Deep Learning

## Overview

This project is a **Blockchain-Assisted Deepfake Video Detection System** that combines Deep Learning and Ethereum Blockchain for secure, tamper-proof video authentication.

The system uses **ResNeXt-50 CNN** for spatial feature extraction and **LSTM** for learning temporal patterns across video frames. Detection results are securely stored on a **Private Ethereum Blockchain (Proof of Authority)** for immutable verification.

---

## Features

- Deepfake Video Detection
- Haar Cascade Face Detection
- ResNeXt-50 CNN Feature Extraction
- LSTM Temporal Learning
- Private Ethereum Blockchain Integration (PoA)
- SHA-256 Video Hashing
- Smart Contract Based Verification
- Tamper-Proof Prediction Storage
- React Web Frontend
- Real-time Blockchain Verification

---

## System Workflow

```
Input Video → Face Detection (Haar Cascade) → Frame Preprocessing
→ ResNeXt-50 CNN → LSTM → Deepfake Classification
→ SHA-256 Hash Generation → Private Ethereum Blockchain → Verification
```

---

## Technologies Used

- Python
- PyTorch / TorchVision
- OpenCV
- ResNeXt-50 CNN
- LSTM
- Private Ethereum (Geth v1.13.15)
- Solidity ^0.8.0
- Web3.py
- Hardhat
- React.js
- Flask

---

## Dataset

Dataset used: **FaceForensics++**

| Split | Real Videos | Fake Videos | Total |
|-------|-------------|-------------|-------|
| Train | 700 | 700 | 1400 |
| Test  | 299 | 300 | 599  |
| **Total** | **999** | **1000** | **1999** |

---

## Model Architecture

- **Feature Extractor:** ResNeXt-50 (pretrained on ImageNet, layer4 fine-tuned)
- **Classifier:** 2-layer LSTM (hidden_dim=256, dropout=0.3)
- **Input:** 10 face-cropped frames per video (every 20th frame)
- **Output:** Real / Deepfake + Confidence Score

---

## Results

| Metric | Score |
|--------|-------|
| Accuracy | 93.32% |
| Precision | 93.33% |
| Recall | 93.33% |
| F1-Score | 93.33% |

### Confusion Matrix

|  | Predicted Real | Predicted Fake |
|--|----------------|----------------|
| **Actual Real** | 279 (TN) | 20 (FP) |
| **Actual Fake** | 20 (FN) | 280 (TP) |

---

## Blockchain Storage

The following information is stored on the Private Ethereum Blockchain:

- SHA-256 Video Hash
- Prediction Result (Real / Deepfake)
- Confidence Score
- Detector (ResNeXt+LSTM)
- Timestamp
- Blockchain Transaction ID

This provides an **immutable and verifiable record** of every prediction.

### Blockchain Configuration

| Parameter | Value |
|-----------|-------|
| Network | Private Ethereum |
| Consensus | Proof of Authority (Clique) |
| Chain ID | 2025 |
| Block Time | ~3 seconds |
| Smart Contract | DeepfakeVerifier.sol |

---

## Project Structure

```
Deepfake-Project/
├── backend/
│   ├── app.py                  # Flask API
│   ├── model.py                # ResNeXt + LSTM architecture
│   ├── blockchain.py           # Web3 blockchain integration
│   ├── train_lstm.py           # LSTM training script
│   ├── extract_features.py     # Feature extraction from videos
│   └── requirements.txt        # Python dependencies
├── blockchain/
│   ├── contracts/
│   │   └── DeepfakeVerifier.sol  # Smart contract
│   ├── scripts/
│   │   └── deploy.js           # Deployment script
│   ├── genesis.json            # PoA genesis block
│   └── hardhat.config.js       # Hardhat configuration
└── frontend/
    ├── src/
    │   ├── App.js              # Main React app
    │   ├── Upload.js           # Video upload component
    │   └── Metrics.js          # Performance metrics tab
    └── public/
        └── index.html
```

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/upload` | Upload video for detection + blockchain logging |
| GET | `/verify?hash=<hash>` | Verify result on blockchain |
| GET | `/health` | Health check (Flask + Blockchain) |

---

## How to Run

### 1. Start Blockchain Node
```bash
cd blockchain/node1
geth --datadir . --networkid 2025 --http --http.addr 0.0.0.0 --http.port 8545 \
     --http.api eth,net,web3,personal --allow-insecure-unlock \
     --unlock 0x557C00620eCdcDE7dAc0722b0Cf6b26c434733C3 \
     --password password.txt --mine \
     --miner.etherbase 0x557C00620eCdcDE7dAc0722b0Cf6b26c434733C3 \
     --nodiscover --syncmode full --gcmode archive
```

### 2. Start Backend (Flask API)
```bash
cd backend
py -3.11 app.py
```

### 3. Start Frontend (React)
```bash
cd frontend
npm install
npm start
```

Open `http://localhost:3000` in your browser.

---

## Future Improvements

- Real-Time Detection
- IPFS Integration for video storage
- Mobile Application Support
- Multi-Blockchain Support
- Explainable AI Features
- Federated Learning Integration

---

## Authors

Developed as a B.Tech Final Year Project on Deepfake Detection using Blockchain and Deep Learning.

Saanvi J Shetty

S Skanda Adiga

**Department of Information Science and Engineering**

---

## Reference

P. Senthil Pandian et al., "Blockchain-Assisted Video Integrity Verification Using ResNeXt and LSTM-Based Deepfake Detection," *International Journal of Basic and Applied Sciences*, 14(4), 2025, pp. 802-807.
