import React, { useState, useEffect } from "react";
import LoginPage from "./components/LoginPage.jsx";
import ProfilePage from "./components/ProfilePage.jsx";
import WellnessPage from "./components/WellnessPage.jsx";
import logo from "./assets/arogya-logo.jpeg";

function App() {
  // Track which user is currently logged in (empty string means not logged in)
  const [userId, setUserId] = useState("");
  // Track whether the user has completed the basic health profile
  const [profileCompleted, setProfileCompleted] = useState(false);

  // Set the browser tab title once when the app mounts
  useEffect(() => {
    document.title = "Arogya Wellness Assistant";
  }, []);

  // Decide which main page to render based on auth/profile state
  let content;
  if (!userId) {
    // Step 1: No user logged in → show login screen
    content = (
      <LoginPage
        onLogin={(uid) => {
          // After successful login, store the username as userId
          setUserId(uid);
        }}
      />
    );
  } else if (!profileCompleted) {
    // Step 2: User logged in but profile not completed → show profile screen
    content = (
      <ProfilePage
        userId={userId}
        onProfileSaved={() => setProfileCompleted(true)}
      />
    );
  } else {
    // Step 3: User logged in and profile completed → show main wellness UI
    content = (
      <WellnessPage
        userId={userId}
        onLogout={() => {
          // Reset all state on logout
          setUserId("");
          setProfileCompleted(false);
        }}
      />
    );
  }

  return (
    <>
      {/* Top navigation bar with logo and product name */}
      <nav className="app-nav">
        <div className="app-nav-inner">
          {/* Brand block: logo + title */}
          <span className="brand">
            <img src={logo} alt="Arogya logo" className="brand-logo" />
            <span>
              Arogya <span className="brand-accent">Wellness Assistant</span>
            </span>
          </span>

          {/* Short product tagline on the right */}
          <span className="brand-tagline">
            Multi‑agent lifestyle, diet &amp; fitness guidance
          </span>
        </div>
      </nav>

      {/* Render the active page (login / profile / wellness) */}
      {content}
    </>
  );
}

export default App;
