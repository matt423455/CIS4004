import React, { useState } from 'react';
import '../styles/SignUp.css'; 
const SignUp = ({ onBackToLogin }) => {
  const [formData, setFormData] = useState({
    firstName: '',
    lastName: '',
    email: '',
    username: '',
    password: '',
    confirmPassword: ''
  });
  
  const [errors, setErrors] = useState({});
  
  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value
    });
    
    // Clear error when typing
    if (errors[name]) {
      setErrors({
        ...errors,
        [name]: null
      });
    }
  };
  
  const validate = () => {
    const newErrors = {};
    
    if (!formData.firstName.trim()) {
      newErrors.firstName = 'First name is required';
    }
    
    if (!formData.lastName.trim()) {
      newErrors.lastName = 'Last name is required';
    }
    
    if (!formData.email.trim()) {
      newErrors.email = 'Email is required';
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      newErrors.email = 'Email is invalid';
    }
    
    if (!formData.username.trim()) {
      newErrors.username = 'Username is required';
    } else if (formData.username.length < 4) {
      newErrors.username = 'Username must be at least 4 characters';
    }
    
    if (!formData.password) {
      newErrors.password = 'Password is required';
    } else if (formData.password.length < 6) {
      newErrors.password = 'Password must be at least 6 characters';
    }
    
    if (formData.password !== formData.confirmPassword) {
      newErrors.confirmPassword = 'Passwords do not match';
    }
    
    return newErrors;
  };
  
  const handleSubmit = (e) => {
    e.preventDefault();
    
    const validationErrors = validate();
    if (Object.keys(validationErrors).length > 0) {
      setErrors(validationErrors);
      return;
    }
    
    // In a real app, you would handle signup API call here
    console.log('Sign up data:', formData);
    alert('Account created successfully! You can now log in.');
    if (onBackToLogin) onBackToLogin();
  };
  
  return (
    <div className="signup-container">
      <div className="form-header">
        <button className="close-button" onClick={onBackToLogin}>
          ×
        </button>
        <h2 className="form-title">Create Account</h2>
        <p className="form-subtitle">Join Paradise Trivia today</p>
      </div>
      
      <form onSubmit={handleSubmit}>
        <div className="form-row">
          <div className="form-col">
            <label className="form-label">First Name</label>
            <input
              className="form-input"
              type="text"
              name="firstName"
              value={formData.firstName}
              onChange={handleChange}
              placeholder="First Name"
            />
            {errors.firstName && <div className="error-text">{errors.firstName}</div>}
          </div>
          
          <div className="form-col">
            <label className="form-label">Last Name</label>
            <input
              className="form-input"
              type="text"
              name="lastName"
              value={formData.lastName}
              onChange={handleChange}
              placeholder="Last Name"
            />
            {errors.lastName && <div className="error-text">{errors.lastName}</div>}
          </div>
        </div>
        
        <div className="form-group">
          <label className="form-label">Email</label>
          <input
            className="form-input"
            type="email"
            name="email"
            value={formData.email}
            onChange={handleChange}
            placeholder="Your email address"
          />
          {errors.email && <div className="error-text">{errors.email}</div>}
        </div>
        
        <div className="form-group">
          <label className="form-label">Username</label>
          <input
            className="form-input"
            type="text"
            name="username"
            value={formData.username}
            onChange={handleChange}
            placeholder="Choose a username"
          />
          {errors.username && <div className="error-text">{errors.username}</div>}
        </div>
        
        <div className="form-group">
          <label className="form-label">Password</label>
          <input
            className="form-input"
            type="password"
            name="password"
            value={formData.password}
            onChange={handleChange}
            placeholder="Create a password"
          />
          {errors.password && <div className="error-text">{errors.password}</div>}
        </div>
        
        <div className="form-group">
          <label className="form-label">Confirm Password</label>
          <input
            className="form-input"
            type="password"
            name="confirmPassword"
            value={formData.confirmPassword}
            onChange={handleChange}
            placeholder="Confirm your password"
          />
          {errors.confirmPassword && <div className="error-text">{errors.confirmPassword}</div>}
        </div>
        
        
        <button type="submit" className="signup-button">
          Create Account
        </button>
      </form>
      
      
    </div>
  );
};

export default SignUp;