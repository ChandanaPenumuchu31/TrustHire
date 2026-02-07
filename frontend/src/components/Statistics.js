import React, { useEffect, useState } from 'react';
import { getStatistics } from '../services/api';
import './Statistics.css';

function Statistics() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    setLoading(true);
    try {
      const response = await getStatistics();
      setStats(response.stats);
    } catch (error) {
      console.error('Failed to load statistics');
    } finally {
      setLoading(false);
    }
  };

  if (loading || !stats) return null;

  return (
    <div className="statistics-container">
      <h2 className="stats-title">📊 Platform Statistics</h2>
      
      <div className="stats-grid">
        <div className="stat-card">
          <span className="stat-icon">📝</span>
          <div className="stat-info">
            <span className="stat-value">{stats.total_jobs?.toLocaleString() || 0}</span>
            <span className="stat-label">Total Jobs Analyzed</span>
          </div>
        </div>

        <div className="stat-card">
          <span className="stat-icon">✅</span>
          <div className="stat-info">
            <span className="stat-value">{stats.active_jobs?.toLocaleString() || 0}</span>
            <span className="stat-label">Active Listings</span>
          </div>
        </div>

        <div className="stat-card">
          <span className="stat-icon">⚠️</span>
          <div className="stat-info">
            <span className="stat-value">{stats.fraudulent_jobs?.toLocaleString() || 0}</span>
            <span className="stat-label">Fraudulent Detected</span>
          </div>
        </div>

        <div className="stat-card">
          <span className="stat-icon">🛡️</span>
          <div className="stat-info">
            <span className="stat-value">{stats.fraud_rate?.toFixed(1) || 0}%</span>
            <span className="stat-label">Fraud Rate</span>
          </div>
        </div>
      </div>

      {stats.popular_searches && stats.popular_searches.length > 0 && (
        <div className="popular-searches">
          <h3>🔥 Trending Searches</h3>
          <div className="search-tags">
            {stats.popular_searches.slice(0, 8).map((search, idx) => (
              <span key={idx} className="search-tag">
                {search.query} ({search.count})
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default Statistics;
