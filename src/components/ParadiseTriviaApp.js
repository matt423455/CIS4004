import React, { useState } from 'react';
import Login from './Login';
import SignUp from './SignUp';
import '../styles/ParadiseTriviaApp.css';

const ParadiseTriviaApp = () => {
  const [showLoginForm, setShowLoginForm] = useState(false);
  const [showLanding, setShowLanding] = useState(true);
  const [showSignUp, setShowSignUp] = useState(false);

  const handleLoginClick = () => {
    // First, fade out the landing content
    setShowLanding(false);
    
    // Then, after a delay, show the login form
    setTimeout(() => {
      setShowLoginForm(true);
    }, 500); // 500ms delay for the transition
  };
  
  const handleSignUpClick = () => {
    setShowLoginForm(false);
    setShowSignUp(true);
  };
  
  const handleBackToLogin = () => {
    setShowSignUp(false);
    setShowLoginForm(true);
  };

  return (
    <div className="app-container">
      {/* Background decorative elements */}
      <div className="background-decoration">
        <div className="decoration-circle-1"></div>
        <div className="decoration-circle-2"></div>
        
        {/* Abstract shapes */}
        <svg className="abstract-lines" viewBox="0 0 1000 1000">
          <path d="M0,300 Q200,250 300,350 T500,300 T700,350 T1000,300" stroke="#F27BBD" strokeWidth="8" fill="none" />
          <path d="M0,600 Q200,650 300,550 T500,600 T700,550 T1000,600" stroke="#874CCC" strokeWidth="8" fill="none" />
        </svg>
      </div>

      <div className="content-container">
        {showLanding && (
          // Initial landing view
          <div className={`landing-view ${!showLanding ? 'fade-out' : ''}`}>
            <div className="logo-container">
              <h1 className="title">PARADISE TRIVIA</h1>
              <div className="subtitle">ENTERTAINMENT</div>
            </div>

            <div className="button-container">
              <button className="login-button" onClick={handleLoginClick}>
                LOG IN
              </button>
            </div>
          </div>
        )}
        
        {showLoginForm && !showSignUp && (
          <Login onSignUpClick={handleSignUpClick} />
        )}
        
        {showSignUp && (
          <SignUp onBackToLogin={handleBackToLogin} />
        )}
      </div>
    </div>
  );
};

export default ParadiseTriviaApp;