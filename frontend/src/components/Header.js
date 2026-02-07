import React from 'react';
import './Header.css';

function Header() {
  return (
    <header className="header">
      <div className="header-content">
        <div className="logo">
          <span className="logo-icon">🛡️</span>
          <h1>TrustHire</h1>
        </div>
        <nav className="nav">
          <span className="nav-tagline">AI-Powered Job Search with Fraud Detection</span>
        </nav>
      </div>
    </header>
  );
}

export default Header;
