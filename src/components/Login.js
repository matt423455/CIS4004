import React, { useState } from 'react';
// import { Link } from 'react-router-dom'; 
import '../styles/LoginPage.css'; 

const Login = ({ onSignUpClick }) => {
  return (
    <div className="login-form-container">
      <div className="form-header">
        <h2 className="form-title">Welcome</h2>
        <p className="form-subtitle">Sign in to continue to Paradise Trivia</p>
      </div>

      <div className="form-group">
        <label className="form-label">Username</label>
        <input 
          className="form-input"
          type="text" 
          placeholder="Enter your username" 
        />
      </div>

      <div className="form-group">
        <label className="form-label">Password</label>
        <input 
          className="form-input"
          type="password" 
          placeholder="Enter your password" 
        />
      </div>

      <button className="sign-in-button">SIGN IN</button>
      
      <div className="divider">
        <div className="divider-line"></div>
        <span className="divider-text">OR</span>
      </div>
      
      <button className="create-account-button" onClick={onSignUpClick}>CREATE ACCOUNT</button>

      <div className="form-links">
        <a className="form-link">Forgot password?</a>
        <a className="form-link" onClick={onSignUpClick}>Sign up</a>
      </div>
    </div>
  );
};

export default Login;