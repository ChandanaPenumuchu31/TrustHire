import React, { useState } from 'react';
import './JobCard.css';

function JobCard({ job }) {
  const [expanded, setExpanded] = useState(false);
  const [showReportForm, setShowReportForm] = useState(false);
  const [showDetailedReasons, setShowDetailedReasons] = useState(false);

  const getTrustColor = (score) => {
    if (score >= 0.7) return '#4caf50';
    if (score >= 0.5) return '#ff9800';
    return '#f44336';
  };

  const getTrustLabel = (score) => {
    if (score >= 0.7) return 'Trusted';
    if (score >= 0.5) return 'Moderate';
    return 'Caution';
  };

  const getPlatformIcon = (platform) => {
    const icons = {
      'linkedin': '💼',
      'indeed': '🔵',
      'naukri': '🟢',
      'careers': '🏢',
      'government': '🏛️'
    };
    return icons[platform] || '📋';
  };

  return (
    <div className={`job-card ${job.is_fraudulent ? 'flagged' : ''}`}>
      {job.is_fraudulent && (
        <div className="fraud-banner">
          ⚠️ WARNING: This job has been flagged as potentially fraudulent
        </div>
      )}

      <div className="job-header">
        <div className="job-main-info">
          <h3 className="job-title">{job.title}</h3>
          <div className="job-meta">
            <span className="company">🏢 {job.company}</span>
            <span className="location">📍 {job.location}</span>
            {job.salary && <span className="salary">💰 {job.salary}</span>}
            {job.experience_required && (
              <span className="experience">⏱️ {job.experience_required}</span>
            )}
          </div>
        </div>

        <div className="job-trust-score">
          <div 
            className="trust-circle" 
            style={{ 
              background: `conic-gradient(${getTrustColor(job.trust_score)} ${job.trust_score * 360}deg, #e0e0e0 0deg)` 
            }}
          >
            <div className="trust-inner">
              <span className="trust-value">{Math.round(job.trust_score * 100)}</span>
              <span className="trust-percent">%</span>
            </div>
          </div>
          <span 
            className="trust-label" 
            style={{ color: getTrustColor(job.trust_score) }}
          >
            {getTrustLabel(job.trust_score)}
          </span>
        </div>
      </div>

      <div className="job-body">
        <p className="job-description">
          {expanded 
            ? job.description 
            : job.description?.substring(0, 200) + (job.description?.length > 200 ? '...' : '')
          }
        </p>
        
        {job.description?.length > 200 && (
          <button 
            className="expand-btn" 
            onClick={() => setExpanded(!expanded)}
          >
            {expanded ? 'Show Less' : 'Read More'}
          </button>
        )}

        {/* Detailed Fraud Reasons - NEW */}
        {job.detailed_reasons && job.detailed_reasons.length > 0 && (
          <div className="detailed-fraud-analysis">
            <div className="fraud-header" onClick={() => setShowDetailedReasons(!showDetailedReasons)}>
              <strong>🔍 Fraud Analysis Details</strong>
              <span className="toggle-icon">{showDetailedReasons ? '▼' : '▶'}</span>
            </div>
            {showDetailedReasons && (
              <div className="fraud-details">
                {job.detailed_reasons.map((reason, idx) => (
                  <div key={idx} className="fraud-reason-item">
                    {reason}
                  </div>
                ))}
                
                {/* Employee Reviews - Display actual review samples */}
                {job.company_verification?.reviews?.samples && job.company_verification.reviews.samples.length > 0 && (
                  <div className="verification-section review-samples">
                    <strong>💬 Employee Reviews ({job.company_verification.reviews.total_reviews || 0} total):</strong>
                    <div className="review-rating">
                      ⭐ {job.company_verification.reviews.average_rating}/5.0 
                      {job.company_verification.reviews.sentiment && (
                        <span className="sentiment"> • {job.company_verification.reviews.sentiment}</span>
                      )}
                    </div>
                    <div className="review-list">
                      {job.company_verification.reviews.samples.slice(0, 3).map((review, idx) => (
                        <div key={idx} className="review-item">
                          <span className="review-icon">💭</span>
                          <span className="review-text">"{review}"</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        )}

        {job.fraud_signals && job.fraud_signals.length > 0 && (
          <div className="fraud-signals">
            <strong>⚠️ Warning Signs Detected:</strong>
            <ul>
              {job.fraud_signals.map((signal, idx) => (
                <li key={idx}>{signal}</li>
              ))}
            </ul>
          </div>
        )}
      </div>

      <div className="job-footer">
        <div className="job-tags">
          <span className="tag platform-tag">
            {getPlatformIcon(job.platform)} {job.platform}
          </span>
          {job.job_type && <span className="tag">{job.job_type}</span>}
        </div>

        <div className="job-actions">
          <a 
            href={job.url} 
            target="_blank" 
            rel="noopener noreferrer" 
            className="btn btn-primary"
          >
            View Original Job
          </a>
          <button 
            className="btn btn-secondary"
            onClick={() => setShowReportForm(!showReportForm)}
          >
            🚩 Report Fraud
          </button>
        </div>
      </div>

      {showReportForm && (
        <div className="report-form">
          <h4>Report this job as fraudulent</h4>
          <p className="report-help">Help the community by reporting suspicious job postings</p>
          <textarea 
            placeholder="Please describe why you think this job is fraudulent (e.g., asks for money upfront, suspicious company name, unrealistic salary promises)..."
            rows="4"
          />
          <div className="report-actions">
            <button className="btn btn-primary btn-sm">Submit Report</button>
            <button 
              className="btn btn-secondary btn-sm"
              onClick={() => setShowReportForm(false)}
            >
              Cancel
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

export default JobCard;
