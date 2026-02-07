import React, { useState } from 'react';
import { searchJobs } from '../services/api';
import './SearchBar.css';

function SearchBar({ onSearch, onLoading }) {
  const [query, setQuery] = useState('');
  const [location, setLocation] = useState('');
  const [experience, setExperience] = useState('');
  const [selectedPlatforms, setSelectedPlatforms] = useState(['all']);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!query.trim()) {
      setError('Please enter a job title or keyword');
      return;
    }

    setError('');
    onLoading(true);

    try {
      const result = await searchJobs(query, location, experience, selectedPlatforms);
      onSearch(result.jobs || []);
    } catch (err) {
      setError('Failed to search jobs. Please try again.');
      console.error(err);
    } finally {
      onLoading(false);
    }
  };

  const togglePlatform = (platform) => {
    if (platform === 'all') {
      setSelectedPlatforms(['all']);
    } else {
      const newPlatforms = selectedPlatforms.includes('all')
        ? [platform]
        : selectedPlatforms.includes(platform)
        ? selectedPlatforms.filter(p => p !== platform)
        : [...selectedPlatforms, platform];
      
      setSelectedPlatforms(newPlatforms.length === 0 ? ['all'] : newPlatforms);
    }
  };

  return (
    <div className="search-bar-container">
      <form className="search-bar" onSubmit={handleSubmit}>
        <div className="search-inputs">
          <div className="input-group">
            <label>🔍 Job Title / Keywords *</label>
            <input
              type="text"
              placeholder="e.g., Software Engineer, Data Analyst..."
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              className="input-field"
            />
          </div>

          <div className="input-group">
            <label>📍 Location</label>
            <input
              type="text"
              placeholder="e.g., San Francisco, Remote..."
              value={location}
              onChange={(e) => setLocation(e.target.value)}
              className="input-field"
            />
          </div>

          <div className="input-group">
            <label>💼 Experience Level</label>
            <select
              value={experience}
              onChange={(e) => setExperience(e.target.value)}
              className="input-field"
            >
              <option value="">Any</option>
              <option value="entry">Entry Level (0-1 years)</option>
              <option value="mid">Mid Level (2-5 years)</option>
              <option value="senior">Senior Level (5+ years)</option>
            </select>
          </div>
        </div>

        <div className="platform-selector">
          <label>Platforms:</label>
          <div className="platform-buttons">
            {['all', 'linkedin', 'indeed', 'naukri'].map((platform) => (
              <button
                key={platform}
                type="button"
                className={`platform-btn ${selectedPlatforms.includes(platform) ? 'active' : ''}`}
                onClick={() => togglePlatform(platform)}
              >
                {platform === 'all' ? '🌐 All' : platform.charAt(0).toUpperCase() + platform.slice(1)}
              </button>
            ))}
          </div>
        </div>

        {error && <div className="error-message">{error}</div>}

        <button type="submit" className="search-button">
          Search Jobs
        </button>
      </form>
    </div>
  );
}

export default SearchBar;
