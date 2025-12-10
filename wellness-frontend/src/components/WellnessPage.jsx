import React, { useState } from "react";
import axios from "axios";
import ReactMarkdown from "react-markdown";
import { API_BASE_URL } from "../config.js";

function WellnessPage({ userId, onLogout }) {
  const [symptoms, setSymptoms] = useState("");
  const [report, setReport] = useState("");
  const [mode, setMode] = useState("full");
  const [status, setStatus] = useState("");
  const [recommendations, setRecommendations] = useState([]);
  const [summary, setSummary] = useState("");

  const [followUp, setFollowUp] = useState("");
  const [followUpStatus, setFollowUpStatus] = useState("");
  const [followUpAnswer, setFollowUpAnswer] = useState("");

  // agent communication view
  const [showAgents, setShowAgents] = useState(false);
  const [symptomAnalysis, setSymptomAnalysis] = useState("");
  const [lifestyleNotes, setLifestyleNotes] = useState("");
  const [dietNotes, setDietNotes] = useState("");
  const [fitnessNotes, setFitnessNotes] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!symptoms.trim()) {
      setStatus("Please enter symptoms.");
      return;
    }
    setStatus("Processing your request...");
    setRecommendations([]);
    setSummary("");
    setFollowUp("");
    setFollowUpAnswer("");
    setFollowUpStatus("");
    setShowAgents(false);
    setSymptomAnalysis("");
    setLifestyleNotes("");
    setDietNotes("");
    setFitnessNotes("");

    const path = mode === "full" || mode === "agents"
      ? "/health-assist"
      : "/recommendations";

    try {
      const res = await axios.post(`${API_BASE_URL}${path}`, {
        symptoms,
        medical_report: report,
        user_id: userId,
      });

      const data = res.data;

      // always capture agent outputs when health-assist is used
      if (path === "/health-assist") {
        setSymptomAnalysis(data.symptom_analysis || "");
        setLifestyleNotes(data.lifestyle || "");
        setDietNotes(data.diet || "");
        setFitnessNotes(data.fitness || "");
      }

      setRecommendations(data.recommendations || []);
      if (mode === "full") {
        setSummary(data.synthesized_guidance || data.final_summary || "");
      } else if (mode === "agents") {
        setSummary(""); // hide synthesized summary for this mode
        setShowAgents(true);
      }

      setStatus("Guidance generated.");
    } catch (err) {
      setStatus(`Error: ${err.response?.data?.error || err.message}`);
    }
  };

  const handleFollowUp = async (e) => {
    e.preventDefault();
    if (!followUp.trim()) {
      setFollowUpStatus("Please enter a follow-up question.");
      return;
    }
    setFollowUpStatus("Thinking...");
    setFollowUpAnswer("");

    try {
      const res = await axios.post(`${API_BASE_URL}/follow-up`, {
        user_id: userId,
        question: followUp,
      });
      setFollowUpAnswer(res.data.answer || "");
      setFollowUpStatus("Answer generated.");
    } catch (err) {
      setFollowUpStatus(
        `Error: ${err.response?.data?.error || err.message}`
      );
    }
  };

  return (
    <div className="page">
      <header className="top-bar">
        <div>
          <h2>Arogya Wellness Assistant</h2>
          <p className="subtitle">
            Logged in as <strong>{userId}</strong>
          </p>
        </div>
        <button className="secondary-btn" onClick={onLogout}>
          Logout
        </button>
      </header>

      <div className="layout">
        <div className="card">
          <h3>Your Current Health Concern</h3>
          <form onSubmit={handleSubmit}>
            <div className="field">
              <label>Symptoms</label>
              <textarea
                rows={4}
                value={symptoms}
                onChange={(e) => setSymptoms(e.target.value)}
                placeholder="Describe what you are feeling... e.g. mild chest pain after climbing stairs"
              />
            </div>
            <div className="field">
              <label>Medical Report (optional)</label>
              <textarea
                rows={4}
                value={report}
                onChange={(e) => setReport(e.target.value)}
                placeholder="Paste any lab report or doctor's note to give more context."
              />
            </div>
            <div className="field">
              <label>Output Type</label>
              <div className="radio-row">
                <label>
                  <input
                    type="radio"
                    value="full"
                    checked={mode === "full"}
                    onChange={() => setMode("full")}
                  />
                  Full wellness plan
                </label>
                <label>
                  <input
                    type="radio"
                    value="reco"
                    checked={mode === "reco"}
                    onChange={() => setMode("reco")}
                  />
                  Recommendations only
                </label>
                <label>
                  <input
                    type="radio"
                    value="agents"
                    checked={mode === "agents"}
                    onChange={() => setMode("agents")}
                  />
                  Can you show this agent communication?
                </label>
              </div>
            </div>
            {status && <p className="status-text">{status}</p>}
            <button type="submit" className="primary-btn">
              Generate Guidance
            </button>
          </form>
        </div>

        <div className="card">
          <h3>Your Personalized Guidance</h3>
          {mode !== "agents" && recommendations.length > 0 && (
            <div className="block">
              <h4>Key Recommendations</h4>
              <ul>
                {recommendations.map((r, idx) => (
                  <li key={idx}>{r}</li>
                ))}
              </ul>
            </div>
          )}
          {mode !== "agents" && summary && (
            <div className="block">
              <h4>Detailed Summary</h4>
              <div className="summary-pre">
                <ReactMarkdown>{summary}</ReactMarkdown>
              </div>
            </div>
          )}
          {mode !== "agents" && recommendations.length === 0 && !summary && (
            <p className="subtitle">
              Submit your symptoms to see a tailored wellness plan here.
            </p>
          )}

          {showAgents && (
            <div className="block">
              <h4>Agent Communication</h4>

              <div className="block">
                <h5>Symptom Agent</h5>
                <div className="summary-pre">
                  <ReactMarkdown>{symptomAnalysis}</ReactMarkdown>
                </div>
              </div>

              <div className="block">
                <h5>Lifestyle Agent</h5>
                <div className="summary-pre">
                  <ReactMarkdown>{lifestyleNotes}</ReactMarkdown>
                </div>
              </div>

              <div className="block">
                <h5>Diet Agent</h5>
                <div className="summary-pre">
                  <ReactMarkdown>{dietNotes}</ReactMarkdown>
                </div>
              </div>

              <div className="block">
                <h5>Fitness Agent</h5>
                <div className="summary-pre">
                  <ReactMarkdown>{fitnessNotes}</ReactMarkdown>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {(summary || recommendations.length > 0) && (
        <div className="card" style={{ marginTop: "1rem" }}>
          <h3>Ask a Follow‑Up Question</h3>
          <form onSubmit={handleFollowUp}>
            <div className="field">
              <label>Your question about this plan</label>
              <textarea
                rows={3}
                value={followUp}
                onChange={(e) => setFollowUp(e.target.value)}
                placeholder="e.g. Can I go to work tomorrow if my cough is mild?"
              />
            </div>
            {followUpStatus && (
              <p className="status-text">{followUpStatus}</p>
            )}
            <button type="submit" className="primary-btn">
              Ask
            </button>
          </form>

          {followUpAnswer && (
            <div className="block" style={{ marginTop: "0.75rem" }}>
              <h4>Follow‑Up Answer</h4>
              <div className="summary-pre">
                <ReactMarkdown>{followUpAnswer}</ReactMarkdown>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default WellnessPage;
