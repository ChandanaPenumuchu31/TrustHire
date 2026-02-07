"""
Fraud Detection Model using Machine Learning
Detects fraudulent job postings using multiple signals and NLP
"""

import re
import pickle
import os
from typing import Dict, List, Tuple
import numpy as np
from sklearn.ensemble import RandomForestClassifier, IsolationForest
from sklearn.feature_extraction.text import TfidfVectorizer
from textblob import TextBlob
import nltk
from datetime import datetime

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)

class FraudDetector:
    """ML-based fraud detection for job postings"""
    
    # Fraud indicators (red flags)
    FRAUD_KEYWORDS = [
        'guaranteed income', 'work from home easy', 'no experience needed',
        'unlimited earning', 'get rich quick', 'investment required',
        'pay upfront', 'registration fee', 'training fee required',
        'western union', 'money transfer', 'cryptocurrency',
        'urgent hiring', 'immediate start', 'act now', 'limited spots',
        'personal information required', 'bank details', 'social security'
    ]
    
    SUSPICIOUS_PATTERNS = [
        r'\$\d{4,6}\+?\s*per\s*(week|day)',  # Unrealistic salary
        r'contact\s*:\s*\d{10}',  # Personal phone numbers
        r'\b[A-Z0-9._%+-]+@(gmail|yahoo|hotmail)\.',  # Free email domains
        r'http://bit\.ly|tinyurl',  # Shortened URLs
    ]
    
    LEGITIMATE_DOMAINS = [
        'linkedin.com', 'indeed.com', 'naukri.com', 'monster.com',
        'glassdoor.com', 'simplyhired.com'
    ]
    
    def __init__(self):
        """Initialize fraud detector"""
        self.vectorizer = TfidfVectorizer(max_features=500, stop_words='english')
        self.model = None
        self.anomaly_detector = IsolationForest(contamination=0.1, random_state=42)
        self.is_trained = False
        
    def extract_features(self, job_data: Dict) -> Dict[str, float]:
        """Extract features for fraud detection"""
        features = {}
        
        text = f"{job_data.get('title', '')} {job_data.get('description', '')} {job_data.get('company', '')}"
        text = text.lower()
        
        # 1. Keyword-based red flags (30% weight)
        fraud_keyword_count = sum(1 for keyword in self.FRAUD_KEYWORDS if keyword in text)
        features['fraud_keywords'] = min(fraud_keyword_count / 5, 1.0)
        
        # 2. Suspicious patterns (20% weight)
        pattern_count = sum(1 for pattern in self.SUSPICIOUS_PATTERNS if re.search(pattern, text, re.IGNORECASE))
        features['suspicious_patterns'] = min(pattern_count / 3, 1.0)
        
        # 3. Text quality analysis (15% weight)
        features['text_quality'] = self._analyze_text_quality(job_data.get('description', ''))
        
        # 4. Company legitimacy (20% weight)
        features['company_legitimacy'] = self._check_company_legitimacy(job_data)
        
        # 5. Salary analysis (10% weight)
        features['salary_suspicious'] = self._analyze_salary(job_data.get('salary', ''))
        
        # 6. URL trust (5% weight)
        features['url_trust'] = self._check_url_trust(job_data.get('url', ''))
        
        return features
    
    def _analyze_text_quality(self, text: str) -> float:
        """Analyze text quality (grammar, spelling, length)"""
        if not text or len(text) < 50:
            return 0.3  # Too short = suspicious
        
        # Check for excessive caps
        if len(text) > 0:
            caps_ratio = sum(1 for c in text if c.isupper()) / len(text)
            if caps_ratio > 0.3:
                return 0.2
        
        # Check for spelling/grammar using TextBlob
        try:
            blob = TextBlob(text[:500])  # First 500 chars
            sentiment = blob.sentiment.polarity
            
            # Extremely positive sentiment might be suspicious
            if sentiment > 0.8:
                return 0.4
        except:
            pass
        
        # Check for proper sentence structure
        sentences = text.split('.')
        if len(sentences) < 3:
            return 0.5
        
        return 0.8  # Good quality
    
    def _check_company_legitimacy(self, job_data: Dict) -> float:
        """Check company legitimacy signals"""
        company = job_data.get('company', '').lower()
        description = job_data.get('description', '').lower()
        
        score = 0.5  # Neutral start
        
        # Generic company names are suspicious
        generic_names = ['hiring company', 'confidential', 'top company', 'leading firm', 'mnc company']
        if any(name in company for name in generic_names):
            score -= 0.3
        
        # Company website mentioned is good
        if 'www.' in description or '.com' in description:
            score += 0.2
        
        # Company details present
        if len(company) > 3 and company != 'n/a':
            score += 0.2
        
        return max(0, min(1, score))
    
    def _analyze_salary(self, salary: str) -> float:
        """Analyze if salary looks suspicious"""
        if not salary:
            return 0.5  # Neutral if no salary
        
        salary = salary.lower()
        
        # Unrealistic promises
        if any(word in salary for word in ['unlimited', 'lakhs per month', 'crores']):
            return 1.0  # Very suspicious
        
        # Check for proper formatting
        if re.search(r'\d+', salary):
            return 0.2  # Has numbers, likely legitimate
        
        return 0.5
    
    def _check_url_trust(self, url: str) -> float:
        """Check if URL is from trusted domain"""
        if not url:
            return 0.3
        
        url = url.lower()
        
        # Check if from legitimate job platform
        for domain in self.LEGITIMATE_DOMAINS:
            if domain in url:
                return 0.9
        
        # Check for shortened URLs (suspicious)
        if 'bit.ly' in url or 'tinyurl' in url:
            return 0.1
        
        return 0.5
    
    def calculate_trust_score(self, features: Dict[str, float]) -> Tuple[float, bool, List[str]]:
        """
        Calculate trust score and detect fraud
        Returns: (trust_score, is_fraudulent, fraud_signals)
        """
        fraud_signals = []
        
        # Weighted scoring
        weights = {
            'fraud_keywords': 0.30,
            'suspicious_patterns': 0.20,
            'text_quality': 0.15,
            'company_legitimacy': 0.20,
            'salary_suspicious': 0.10,
            'url_trust': 0.05
        }
        
        # Calculate fraud probability
        fraud_score = 0
        for feature, value in features.items():
            if feature in weights:
                contribution = value * weights[feature]
                fraud_score += contribution
                
                # Track signals
                if feature == 'fraud_keywords' and value > 0.4:
                    fraud_signals.append('Contains suspicious keywords')
                elif feature == 'suspicious_patterns' and value > 0.3:
                    fraud_signals.append('Suspicious patterns detected')
                elif feature == 'text_quality' and value < 0.4:
                    fraud_signals.append('Poor text quality')
                elif feature == 'company_legitimacy' and value < 0.4:
                    fraud_signals.append('Questionable company information')
                elif feature == 'salary_suspicious' and value > 0.6:
                    fraud_signals.append('Unrealistic salary claims')
                elif feature == 'url_trust' and value < 0.4:
                    fraud_signals.append('Untrusted source URL')
        
        # Trust score is inverse of fraud score
        trust_score = 1.0 - fraud_score
        
        # Determine if fraudulent (60% threshold)
        is_fraudulent = fraud_score > 0.6
        
        return trust_score, is_fraudulent, fraud_signals
    
    def predict(self, job_data: Dict) -> Dict:
        """
        Main prediction method
        Returns fraud analysis results
        """
        # Extract features
        features = self.extract_features(job_data)
        
        # Calculate trust score
        trust_score, is_fraudulent, fraud_signals = self.calculate_trust_score(features)
        
        # Additional checks
        if not job_data.get('company') or len(job_data.get('company', '')) < 2:
            fraud_signals.append('Missing company information')
            trust_score *= 0.8
            is_fraudulent = True
        
        if not job_data.get('description') or len(job_data.get('description', '')) < 100:
            fraud_signals.append('Insufficient job description')
            trust_score *= 0.9
        
        return {
            'trust_score': max(0.0, min(1.0, trust_score)),
            'is_fraudulent': is_fraudulent,
            'fraud_confidence': 1.0 - trust_score if is_fraudulent else 0.0,
            'fraud_signals': fraud_signals,
            'features': features
        }
    
    def batch_predict(self, jobs: List[Dict]) -> List[Dict]:
        """Predict fraud for multiple jobs"""
        results = []
        for job in jobs:
            result = self.predict(job)
            results.append(result)
        return results

# Singleton instance
_fraud_detector = None

def get_fraud_detector() -> FraudDetector:
    """Get or create fraud detector instance"""
    global _fraud_detector
    if _fraud_detector is None:
        _fraud_detector = FraudDetector()
    return _fraud_detector
