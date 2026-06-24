import React, { useState, useRef } from "react";
import "./Upload.css";

const API = "http://localhost:5000";

function Upload() {
  const [file, setFile]         = useState(null);
  const [preview, setPreview]   = useState(null);
  const [loading, setLoading]   = useState(false);
  const [result, setResult]     = useState(null);
  const [verified, setVerified] = useState(null);
  const [error, setError]       = useState(null);
  const inputRef                = useRef();

  const handleFile = (f) => {
    if (!f) return;
    setFile(f);
    setResult(null);
    setVerified(null);
    setError(null);
    setPreview(URL.createObjectURL(f));
  };

  const handleDrop = (e) => {
    e.preventDefault();
    handleFile(e.dataTransfer.files[0]);
  };

  const handleUpload = async () => {
    if (!file) return;
    setLoading(true);
    setError(null);
    setResult(null);
    setVerified(null);

    const form = new FormData();
    form.append("video", file);
    form.append("device", "web-client");

    try {
      const res  = await fetch(`${API}/upload`, { method: "POST", body: form });
      const data = await res.json();
      if (data.error) throw new Error(data.error);
      setResult(data);
    } catch (err) {
      setError(err.message || "Upload failed");
    } finally {
      setLoading(false);
    }
  };

  const handleVerify = async () => {
    if (!result?.video_hash) return;
    try {
      const res  = await fetch(`${API}/verify?hash=${result.video_hash}`);
      const data = await res.json();
      setVerified(data);
    } catch {
      setError("Blockchain verification failed");
    }
  };

  const isFake = result?.result === "Deepfake";

  return (
    <div className="upload-page">

      {/* Upload zone */}
      <div
        className={`drop-zone ${file ? "has-file" : ""}`}
        onDrop={handleDrop}
        onDragOver={(e) => e.preventDefault()}
        onClick={() => inputRef.current.click()}
      >
        <input
          ref={inputRef}
          type="file"
          accept="video/*"
          style={{ display: "none" }}
          onChange={(e) => handleFile(e.target.files[0])}
        />
        {preview ? (
          <video src={preview} className="preview-video" controls />
        ) : (
          <div className="drop-placeholder">
            <span className="drop-icon">🎬</span>
            <p className="drop-label">Drop a video or click to browse</p>
            <p className="drop-hint">MP4, AVI, MOV · max 500 MB</p>
          </div>
        )}
      </div>

      {file && (
        <div className="file-info">
          <span className="file-name">{file.name}</span>
          <span className="file-size">{(file.size / 1024 / 1024).toFixed(1)} MB</span>
        </div>
      )}

      {/* Action button */}
      <button
        className="btn-primary"
        onClick={handleUpload}
        disabled={!file || loading}
      >
        {loading ? (
          <><span className="spinner" /> Analysing video…</>
        ) : (
          "Detect & Log to Blockchain"
        )}
      </button>

      {error && <div className="error-box">⚠ {error}</div>}

      {/* Detection result */}
      {result && (
        <div className={`result-card ${isFake ? "fake" : "real"}`}>
          <div className="result-badge">
            {isFake ? "⚠ DEEPFAKE DETECTED" : "✓ AUTHENTIC VIDEO"}
          </div>
          <div className="result-grid">
            <div className="result-item">
              <span className="item-label">Confidence</span>
              <span className="item-value">{result.confidence}</span>
            </div>
            <div className="result-item">
              <span className="item-label">Device</span>
              <span className="item-value">{result.device}</span>
            </div>
            <div className="result-item full">
              <span className="item-label">Video Hash (SHA-256)</span>
              <span className="item-value mono">{result.video_hash}</span>
            </div>
            <div className="result-item full">
              <span className="item-label">Blockchain TX ID</span>
              <span className="item-value mono">{result.tx_id}</span>
            </div>
          </div>

          <button className="btn-verify" onClick={handleVerify}>
            🔗 Verify on Blockchain
          </button>
        </div>
      )}

      {/* Blockchain verification */}
      {verified && (
        <div className="verify-card">
          <h3 className="verify-title">🔐 Blockchain Record</h3>
          <div className="verify-grid">
            <div className="verify-row">
              <span>Result</span>
              <span className={verified.is_fake ? "tag-fake" : "tag-real"}>
                {verified.result}
              </span>
            </div>
            <div className="verify-row">
              <span>Detector</span>
              <span className="mono">{verified.detector}</span>
            </div>
            <div className="verify-row">
              <span>Timestamp</span>
              <span>{new Date(verified.timestamp * 1000).toLocaleString()}</span>
            </div>
            <div className="verify-row">
              <span>Video Hash</span>
              <span className="mono small">{verified.video_hash}</span>
            </div>
          </div>
          <p className="verify-note">
            ✅ Record immutably stored on private Ethereum blockchain (Chain ID 2025)
          </p>
        </div>
      )}
    </div>
  );
}

export default Upload;