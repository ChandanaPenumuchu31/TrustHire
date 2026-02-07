import React, { useState } from 'react';
import './App.css';
import SearchBar from './components/SearchBar';
import JobList from './components/JobList';
import Statistics from './components/Statistics';
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
            <p>Searching across multiple platforms and analyzing jobs...</p>
          </div>
        )}
        {!loading && searchPerformed && (
          <JobList jobs={jobs} />
        )}
        {!searchPerformed && !loading && (
          <div className="welcome-section">
            <h2>🎯 Welcome to TrustHire</h2>
            <p className="subtitle">Your trusted job search companion</p>
            <div className="features">
              <div className="feature-card">
                <span className="feature-icon">🔍</span>
                <h3>Multi-Platform Search</h3>
                <p>Search across LinkedIn, Indeed, and Naukri in one place</p>
              </div>
              <div className="feature-card">
                <span className="feature-icon">🛡️</span>
                <h3>Fraud Detection</h3>
                <p>AI-powered analysis to identify suspicious job posts</p>
              </div>
              <div className="feature-card">
                <span className="feature-icon">⭐</span>
                <h3>Trust Scores</h3>
                <p>Every job rated for authenticity and reliability</p>
              </div>
              <div className="feature-card">
                <span className="feature-icon">👥</span>
                <h3>Community Reports</h3>
                <p>Help others by reporting fraudulent listings</p>
              </div>
            </div>
          </div>
        )}
        <Statistics />
      </main>
    </div>
  );
}

export default App;
