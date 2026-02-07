from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

db = SQLAlchemy()

class Job(db.Model):
    """Job posting model"""
    __tablename__ = 'jobs'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False, index=True)
    company = db.Column(db.String(200), nullable=False, index=True)
    location = db.Column(db.String(200), nullable=False, index=True)
    description = db.Column(db.Text, nullable=False)
    requirements = db.Column(db.Text)
    salary = db.Column(db.String(100))
    experience_required = db.Column(db.String(50))
    job_type = db.Column(db.String(50))  # Full-time, Part-time, Contract
    
    # Source information
    platform = db.Column(db.String(50), nullable=False, index=True)
    external_id = db.Column(db.String(200))
    url = db.Column(db.String(500), nullable=False)
    
    # Fraud detection scores
    trust_score = db.Column(db.Float, default=0.5)  # 0-1 scale
    is_fraudulent = db.Column(db.Boolean, default=False)
    fraud_confidence = db.Column(db.Float, default=0.0)
    fraud_signals = db.Column(db.Text)  # JSON array of detected signals
    
    # Metadata
    posted_date = db.Column(db.DateTime)
    scraped_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Community features
    views = db.Column(db.Integer, default=0)
    reports = db.Column(db.Integer, default=0)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'title': self.title,
            'company': self.company,
            'location': self.location,
            'description': self.description,
            'requirements': self.requirements,
            'salary': self.salary,
            'experience_required': self.experience_required,
            'job_type': self.job_type,
            'platform': self.platform,
            'url': self.url,
            'trust_score': round(self.trust_score, 2),
            'is_fraudulent': self.is_fraudulent,
            'fraud_confidence': round(self.fraud_confidence, 2),
            'fraud_signals': json.loads(self.fraud_signals) if self.fraud_signals else [],
            'posted_date': self.posted_date.isoformat() if self.posted_date else None,
            'scraped_at': self.scraped_at.isoformat() if self.scraped_at else None,
            'views': self.views,
            'reports': self.reports
        }

class UserReport(db.Model):
    """User fraud reports"""
    __tablename__ = 'user_reports'
    
    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey('jobs.id'), nullable=False)
    reason = db.Column(db.String(500), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    job = db.relationship('Job', backref=db.backref('user_reports', lazy=True))

class SearchHistory(db.Model):
    """Track popular searches"""
    __tablename__ = 'search_history'
    
    id = db.Column(db.Integer, primary_key=True)
    query = db.Column(db.String(200), nullable=False, index=True)
    location = db.Column(db.String(200))
    experience = db.Column(db.String(50))
    count = db.Column(db.Integer, default=1)
    last_searched = db.Column(db.DateTime, default=datetime.utcnow)

def init_db(app):
    """Initialize database"""
    db.init_app(app)
    with app.app_context():
        db.create_all()
