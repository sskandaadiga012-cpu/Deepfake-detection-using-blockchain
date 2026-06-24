import React from "react";
import "./Metrics.css";

// Results from evaluate.py on full dataset
const CM = {
  tp: 280,
  tn: 279,
  fp: 20,
  fn: 20,
};
const total     = CM.tp + CM.tn + CM.fp + CM.fn;
const accuracy  = ((CM.tp + CM.tn) / total * 100).toFixed(2);
const precision = (CM.tp / (CM.tp + CM.fp) * 100).toFixed(2);
const recall    = (CM.tp / (CM.tp + CM.fn) * 100).toFixed(2);
const f1        = (2 * CM.tp / (2 * CM.tp + CM.fp + CM.fn) * 100).toFixed(2);

function Metrics() {
  return (
    <div className="metrics-page">

      {/* Score cards */}
      <div className="score-grid">
        <div className="score-card">
          <span className="score-label">Accuracy</span>
          <span className="score-value">{accuracy}%</span>
          <span className="score-sub">Overall correct predictions</span>
        </div>
        <div className="score-card">
          <span className="score-label">Precision</span>
          <span className="score-value">{precision}%</span>
          <span className="score-sub">Of predicted fakes, actually fake</span>
        </div>
        <div className="score-card">
          <span className="score-label">Recall</span>
          <span className="score-value">{recall}%</span>
          <span className="score-sub">Of actual fakes, correctly found</span>
        </div>
        <div className="score-card accent">
          <span className="score-label">F1-Score</span>
          <span className="score-value">{f1}%</span>
          <span className="score-sub">Harmonic mean of precision & recall</span>
        </div>
      </div>

      {/* Confusion Matrix */}
      <div className="cm-section">
        <h2 className="cm-title">Confusion Matrix</h2>
        <p className="cm-sub">Evaluated on test set · 600 videos</p>

        <div className="cm-wrap">
          <div className="cm-table">

            {/* Header row */}
            <div />
            <div className="cm-head">Predicted Real</div>
            <div className="cm-head">Predicted Fake</div>

            {/* Row 1 — Actual Real */}
            <div className="cm-row-label">Actual Real</div>
            <div className="cm-cell correct">
              <span className="cm-num">{CM.tn}</span>
              <span className="cm-tag">True Negative</span>
            </div>
            <div className="cm-cell wrong">
              <span className="cm-num">{CM.fp}</span>
              <span className="cm-tag">False Positive</span>
            </div>

            {/* Row 2 — Actual Fake */}
            <div className="cm-row-label">Actual Fake</div>
            <div className="cm-cell wrong">
              <span className="cm-num">{CM.fn}</span>
              <span className="cm-tag">False Negative</span>
            </div>
            <div className="cm-cell correct">
              <span className="cm-num">{CM.tp}</span>
              <span className="cm-tag">True Positive</span>
            </div>

          </div>
        </div>

        {/* Legend */}
        <div className="cm-legend">
          <div className="legend-item">
            <span className="legend-dot correct-dot" />
            <span>Correct prediction</span>
          </div>
          <div className="legend-item">
            <span className="legend-dot wrong-dot" />
            <span>Incorrect prediction</span>
          </div>
        </div>
      </div>

      {/* Dataset info */}
      <div className="dataset-info">
        <h3>Dataset & Training Details</h3>
        <div className="info-grid">
          <div className="info-item"><span>Dataset</span><span>FaceForensics++</span></div>
          <div className="info-item"><span>Total Videos</span><span>{total}</span></div>
          <div className="info-item"><span>Fake Videos</span><span>{CM.tp + CM.fn}</span></div>
          <div className="info-item"><span>Real Videos</span><span>{CM.tn + CM.fp}</span></div>
          <div className="info-item"><span>Train/Test Split</span><span>70% / 30%</span></div>
          <div className="info-item"><span>Feature Extractor</span><span>ResNeXt-50</span></div>
          <div className="info-item"><span>Classifier</span><span>LSTM (2-layer)</span></div>
          <div className="info-item"><span>Blockchain</span><span>Private Ethereum PoA</span></div>
        </div>
      </div>

    </div>
  );
}

export default Metrics;