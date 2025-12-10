import React, { useState } from "react";
import axios from "axios";
import { API_BASE_URL } from "../config.js";
import logo from "../assets/arogya-logo.jpeg";

function LoginPage({ onLogin }) {
  const [mode, setMode] = useState("login"); // "login" or "register"
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [info, setInfo] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!username.trim()) {
      setError("Please enter a username.");
      return;
    }
    if (!password.trim()) {
      setError("Please enter a password.");
      return;
    }

    setError("");
    setInfo("");
    setLoading(true);

    const path = mode === "register" ? "/register" : "/login";

    try {
      const res = await axios.post(`${API_BASE_URL}${path}`, {
        username: username.trim(),
        password: password.trim(),
      });

      if (res.status === 200 && res.data?.status === "ok") {
        if (mode === "register") {
          setInfo("Account created. You can now log in.");
          setMode("login");
        } else {
          onLogin(res.data.user_id);
        }
      } else {
        setError(res.data?.error || "Unable to process request. Please try again.");
      }
    } catch (err) {
      setError(err.response?.data?.error || "Unable to process request. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page">
      <div className="card auth-card">
        <div
          style={{
            display: "flex",
            alignItems: "center",
            marginBottom: "1rem",
          }}
        >
          <img
            src={logo}
            alt="Arogya logo"
            style={{
              height: 100,
              width: 100,
              borderRadius: "999px",
              marginRight: 20,
              objectFit: "contain",
            }}
          />
          <h1 style={{ margin: 0, fontSize: "2.25rem", lineHeight: 1.15 }}>
            Arogya Wellness
            <br />
            Assistant
          </h1>
        </div>
        <p className="subtitle">
          {mode === "login" ? "Log in to continue." : "Create your account to get started."}
        </p>
        <form onSubmit={handleSubmit}>
          <div className="field">
            <label>Username</label>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="Enter your username"
            />
          </div>
          <div className="field">
            <label>Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Enter your password"
            />
          </div>
          {error && <p className="error">{error}</p>}
          {info && <p className="status-text">{info}</p>}
          <button type="submit" className="primary-btn" disabled={loading}>
            {loading
              ? mode === "login"
                ? "Logging in..."
                : "Creating account..."
              : mode === "login"
              ? "Continue"
              : "Register"}
          </button>
        </form>

        <p className="subtitle" style={{ marginTop: "0.75rem" }}>
          {mode === "login" ? (
            <>
              New to Arogya?{" "}
              <button
                type="button"
                className="link-button"
                onClick={() => {
                  setMode("register");
                  setError("");
                  setInfo("");
                }}
              >
                Create an account
              </button>
            </>
          ) : (
            <>
              Already have an account?{" "}
              <button
                type="button"
                className="link-button"
                onClick={() => {
                  setMode("login");
                  setError("");
                  setInfo("");
                }}
              >
                Log in
              </button>
            </>
          )}
        </p>
      </div>
    </div>
  );
}

export default LoginPage;
