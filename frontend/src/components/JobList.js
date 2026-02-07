import React, { useState } from 'react';
import JobCard from './JobCard';
import './JobList.css';

function JobList({ jobs }) {
  const [filter, setFilter] = useState('all');
  const [sortBy, setSortBy] = useState('trust');

  const filteredJobs = jobs.filter(job => {
    if (filter === 'all') return true;
    if (filter === 'trusted') return job.trust_score >= 0.7;
    if (filter === 'flagged') return job.is_fraudulent;
    return true;
  });

  const sortedJobs = [...filteredJobs].sort((a, b) => {
    if (sortBy === 'trust') return b.trust_score - a.trust_score;
    if (sortBy === 'recent') return new Date(b.scraped_at) - new Date(a.scraped_at);
    return 0;
  });

  if (jobs.length === 0) {
    return (
      <div className="no-results">
        <span className="no-results-icon">🔍</span>
        <h3>No jobs found</h3>
        <p>Try adjusting your search criteria or try different keywords</p>
      </div>
    );
  }

  return (
    <div className="job-list-container">
      <div className="job-list-header">
        <h2>Found {jobs.length} Jobs</h2>
        
        <div className="controls">
          <div className="filter-group">
            <label>Filter:</label>
            <select value={filter} onChange={(e) => setFilter(e.target.value)} className="control-select">
              <option value="all">All Jobs</option>
              <option value="trusted">Trusted (70%+)</option>
              <option value="flagged">Flagged</option>
            </select>
          </div>

          <div className="filter-group">
            <label>Sort:</label>
            <select value={sortBy} onChange={(e) => setSortBy(e.target.value)} className="control-select">
              <option value="trust">Trust Score</option>
              <option value="recent">Most Recent</option>
            </select>
          </div>
        </div>
      </div>

      <div className="job-list">
        {sortedJobs.map((job, index) => (
          <JobCard key={index} job={job} />
        ))}
      </div>

      {sortedJobs.length === 0 && (
        <div className="no-results">
          <p>No jobs match your filters</p>
        </div>
      )}
    </div>
  );
}

export default JobList;
