import React, { useEffect, useState } from "react";
import axios from "axios";
import { API_BASE_URL } from "../config.js";

function ProfilePage({ userId, onProfileSaved }) {
  const [height, setHeight] = useState("");
  const [weight, setWeight] = useState("");
  const [meds, setMeds] = useState("");
  const [status, setStatus] = useState("");

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        const res = await axios.get(`${API_BASE_URL}/profile/${userId}`);
        const p = res.data.profile || {};
        if (p.height_cm) setHeight(String(p.height_cm));
        if (p.weight_kg) setWeight(String(p.weight_kg));
        if (p.medications) setMeds(p.medications);
      } catch {
        // ignore first time
      }
    };
    fetchProfile();
  }, [userId]);

  const handleSave = async (e) => {
    e.preventDefault();
    setStatus("Saving profile...");

    try {
      await axios.post(`${API_BASE_URL}/profile/${userId}`, {
        height_cm: height ? Number(height) : null,
        weight_kg: weight ? Number(weight) : null,
        medications: meds,
      });
      setStatus("Profile saved. You can now ask wellness queries.");
      onProfileSaved();
    } catch (err) {
      setStatus(`Failed to save profile: ${err.message}`);
    }
  };

  return (
    <div className="page">
      <div className="card">
        <h2>Welcome to Arogya, {userId}</h2>
        <p className="subtitle">
          Please provide some basic information to personalize your guidance.
        </p>
        <form onSubmit={handleSave}>
          <div className="field">
            <label>Height (cm)</label>
            <input
              type="number"
              value={height}
              onChange={(e) => setHeight(e.target.value)}
              placeholder="e.g. 170"
            />
          </div>
          <div className="field">
            <label>Weight (kg)</label>
            <input
              type="number"
              value={weight}
              onChange={(e) => setWeight(e.target.value)}
              placeholder="e.g. 65"
            />
          </div>
          <div className="field">
            <label>Medications (past / current)</label>
            <textarea
              rows={4}
              value={meds}
              onChange={(e) => setMeds(e.target.value)}
              placeholder="List medicines you are taking or took recently..."
            />
          </div>
          {status && <p className="status-text">{status}</p>}
          <button type="submit" className="primary-btn">
            Save & Continue
          </button>
        </form>
      </div>
    </div>
  );
}

export default ProfilePage;
