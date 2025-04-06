import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import Login from './components/Login';
import Quiz from './components/Quiz';
import Dashboard from './components/Dashboard';

function App() {
  return (
    <Router>
      <nav style={{ margin: 20 }}>
        <Link to="/" style={{ marginRight: 10 }}>Login</Link>
        <Link to="/quiz" style={{ marginRight: 10 }}>Quiz</Link>
        <Link to="/dashboard">Dashboard</Link>
      </nav>

      <Routes>
        <Route path="/" element={<Login />} />
        <Route path="/quiz" element={<Quiz />} />
        <Route path="/dashboard" element={<Dashboard />} />
      </Routes>
    </Router>
  );
}

export default App;
