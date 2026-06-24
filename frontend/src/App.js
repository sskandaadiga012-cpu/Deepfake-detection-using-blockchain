import React, { useState } from "react";
import Upload from "./Upload";
import Metrics from "./Metrics";
import "./App.css";

function App() {
  const [tab, setTab] = useState("detect");

  return (
    <div className="app">
      <header className="header">
        <div className="header-inner">
          <div className="logo">
            <span className="logo-icon">🔐</span>
            <span className="logo-text">DeepVerify</span>
          </div>
          <p className="header-sub">Blockchain-Assisted Deepfake Detection</p>
        </div>
      </header>

      <nav className="nav">
        <button
          className={`nav-tab ${tab === "detect" ? "active" : ""}`}
          onClick={() => setTab("detect")}
        >
          🎬 Detect
        </button>
        <button
          className={`nav-tab ${tab === "metrics" ? "active" : ""}`}
          onClick={() => setTab("metrics")}
        >
          📊 Metrics
        </button>
      </nav>

      <main className="main">
        {tab === "detect" ? <Upload /> : <Metrics />}
      </main>

      <footer className="footer">
        <p>Powered by ResNeXt + LSTM · Private Ethereum Blockchain · PoA Consensus</p>
      </footer>
    </div>
  );
}

export default App;