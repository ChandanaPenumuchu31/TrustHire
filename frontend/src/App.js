import React, { useState } from 'react';
import './App.css';
import SearchBar from './components/SearchBar';
import JobList from './components/JobList';
import Header from './components/Header';

function App() {
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(false);
  const [searchPerformed, setSearchPerformed] = useState(false);

  const handleSearch = (searchData) => {
    setJobs(searchData);
    setSearchPerformed(true);
  };

  const handleLoading = (isLoading) => {
    setLoading(isLoading);
  };

  return (
    <div className="App">
      <Header />
      <main className="main-content">
        <SearchBar onSearch={handleSearch} onLoading={handleLoading} />
        {loading && (
          <div className="loading-container">
            <div className="spinner"></div>
            <p>Searching across multiple platforms and analyzing jobs for fraud...</p>
          </div>
        )}
        {!loading && searchPerformed && (
          <JobList jobs={jobs} />
        )}
        {!searchPerformed && !loading && (
          <div className="welcome-section">
            <h2>🎯 Welcome to TrustHire</h2>
            <p className="subtitle">Your trusted job search companion with AI-powered fraud detection</p>
            <div className="features">
              <div className="feature-card">
                <span className="feature-icon">🔍</span>
                <h3>Multi-Platform Search</h3>
                <p>Search across RemoteOK and Remotive for remote jobs</p>
              </div>
              <div className="feature-card">
                <span className="feature-icon">🛡️</span>
                <h3>Advanced Fraud Detection</h3>
                <p>AI analyzes job descriptions, company reviews, and salary patterns</p>
              </div>
              <div className="feature-card">
                <span className="feature-icon">⭐</span>
                <h3>Trust Scores</h3>
                <p>Every job rated 0-100% based on company verification and analysis</p>
              </div>
              <div className="feature-card">
                <span className="feature-icon">🏢</span>
                <h3>Company Verification</h3>
                <p>Real-time checks against company databases and online reviews</p>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
