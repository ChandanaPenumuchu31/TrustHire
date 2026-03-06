"""
LLM-Powered Fraud Analyzer using Google Gemini
Uses Gemini AI to analyze job descriptions for fraud patterns with advanced reasoning
"""

try:
    import google.genai as genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False
from typing import Dict, List
import logging
import json
from config import Config

logger = logging.getLogger(__name__)

class LLMFraudAnalyzer:
    """Uses Google Gemini AI for advanced fraud detection"""
    
    def __init__(self):
        """Initialize Gemini AI"""
        self.provider = Config.LLM_PROVIDER
        self.model_name = Config.LLM_MODEL
        self.enabled = False
        
        # Initialize Gemini if enabled
        if not GENAI_AVAILABLE:
            logger.error("google.genai is not installed. Install with: pip install google-genai")
            self.enabled = False
            return

        if self.provider == 'gemini' and Config.GEMINI_API_KEY:
            try:
                # Configure with new API
                client = genai.Client(api_key=Config.GEMINI_API_KEY)
                self.client = client
                self.enabled = True
                logger.info(f"✅ Gemini AI initialized successfully: {self.model_name}")
            except Exception as e:
                logger.error(f"❌ Failed to initialize Gemini: {e}")
                self.enabled = False
        else:
            logger.info("LLM disabled - using rule-based detection only")

    def _model_candidates(self) -> List[str]:
        """Return preferred Gemini models in fallback order."""
        candidates = [
            self.model_name,
            'gemini-2.0-flash',
            'gemini-2.0-flash-lite',
            'gemini-1.5-flash',
            'gemini-1.5-pro',
        ]
        # Preserve order while removing duplicates/empty values.
        seen = set()
        ordered = []
        for model in candidates:
            if model and model not in seen:
                seen.add(model)
                ordered.append(model)
        return ordered
    
    def analyze_job_fraud(self, job_data: Dict, company_reviews: Dict) -> Dict:
        """
        Use Gemini AI to analyze a job posting for fraud
        
        Args:
            job_data: Job information (title, company, description, salary, etc.)
            company_reviews: Real-time scraped reviews from multiple platforms
        
        Returns:
            {
                'fraud_probability': float (0.0 to 1.0),
                'confidence': float (0.0 to 1.0),
                'reasoning': str,
                'red_flags': list,
                'green_flags': list,
                'recommendation': str
            }
        """
        if not self.enabled:
            return self._fallback_analysis(job_data)
        
        try:
            # Build comprehensive prompt for Gemini
            prompt = self._build_fraud_detection_prompt(job_data, company_reviews)
            
            response = None
            last_error = None
            for model in self._model_candidates():
                try:
                    response = self.client.models.generate_content(
                        model=model,
                        contents=prompt
                    )
                    self.model_name = model
                    logger.info(f"✅ Gemini API responded with model: {model}")
                    break
                except Exception as model_error:
                    last_error = model_error
                    logger.warning(f"Gemini model failed ({model}): {model_error}")

            if response is None:
                raise RuntimeError(f"No Gemini models available. Last error: {last_error}")
            
            # Parse Gemini's response
            analysis = self._parse_gemini_response(response.text)
            
            logger.info(f"✅ Gemini analyzed job: {job_data.get('title')} - Fraud probability: {analysis['fraud_probability']:.2%}")
            
            return analysis
            
        except Exception as e:
            logger.error(f"Gemini analysis error: {e}")
            return self._fallback_analysis(job_data)
    
    def _build_fraud_detection_prompt(self, job_data: Dict, company_reviews: Dict) -> str:
        """Build a detailed prompt for Gemini AI"""
        
        prompt = f"""You are an expert fraud detection system analyzing job postings for potential scams. 
Analyze this job posting and provide a detailed fraud assessment.

JOB INFORMATION:
================
Title: {job_data.get('title', 'Unknown')}
Company: {job_data.get('company', 'Unknown')}
Location: {job_data.get('location', 'Unknown')}
Salary: {job_data.get('salary', 'Not specified')}
Job Type: {job_data.get('job_type', 'Not specified')}

DESCRIPTION:
{job_data.get('description', 'No description provided')[:1000]}

REQUIREMENTS:
{job_data.get('requirements', 'Not specified')}

COMPANY REVIEWS (Real-time scraped):
=====================================
Glassdoor: {company_reviews.get('glassdoor', {}).get('rating', 0)}/5.0 ({company_reviews.get('glassdoor', {}).get('reviews', 0)} reviews)
Indeed: {company_reviews.get('indeed', {}).get('rating', 0)}/5.0 ({company_reviews.get('indeed', {}).get('reviews', 0)} reviews)
Google: {company_reviews.get('google', {}).get('rating', 0)}/5.0
AmbitionBox: {company_reviews.get('ambitionbox', {}).get('rating', 0)}/5.0
Average Rating: {company_reviews.get('average_rating', 0)}/5.0
Total Reviews Found: {company_reviews.get('total_reviews', 0)}
Sources Found: {company_reviews.get('sources_found', 0)}
Role Review Evidence Count: {company_reviews.get('role_review_signal', {}).get('evidence_count', 0)}
Role Trusted Domain Hits: {company_reviews.get('role_review_signal', {}).get('trusted_domain_hits', 0)}

ANALYSIS INSTRUCTIONS:
======================
1. Analyze the job description for fraud indicators:
   - Payment requests (registration fees, training fees, advance payments)
   - Unrealistic promises (guaranteed income, easy money, no experience needed)
   - Urgency tactics (limited time, act now, immediate hiring)
   - Personal information requests (bank details, SSN, etc.)
   - Suspicious communication (WhatsApp/Telegram interviews, free email addresses)
   - MLM/pyramid scheme indicators

2. Evaluate company legitimacy:
   - Review ratings and counts from multiple platforms
   - Company name authenticity (avoid generic names like "Confidential", "Top MNC")
   - Professional presentation of job posting

3. Assess salary reasonableness:
   - Compare with industry standards
   - Check for unrealistic pay (e.g., $5000/week for entry-level)
   - Look for daily/weekly pay instead of monthly/annual

4. Check description quality:
   - Grammar and professionalism
   - Clarity of job responsibilities
   - Completeness of information

REQUIRED OUTPUT FORMAT (JSON):
===============================
{{
  "fraud_probability": 0.0-1.0,
  "confidence": 0.0-1.0,
  "reasoning": "Detailed explanation of your analysis",
  "red_flags": ["List of concerning elements found"],
  "green_flags": ["List of positive/legitimate elements found"],
  "recommendation": "SAFE TO APPLY | PROCEED WITH CAUTION | HIGH RISK - DO NOT APPLY"
}}

Provide your analysis as valid JSON only, no additional text."""
        
        return prompt
    
    def _parse_gemini_response(self, response_text: str) -> Dict:
        """Parse Gemini's JSON response"""
        try:
            # Try to extract JSON from response
            # Gemini sometimes wraps JSON in markdown code blocks
            if '```json' in response_text:
                json_start = response_text.find('```json') + 7
                json_end = response_text.find('```', json_start)
                json_text = response_text[json_start:json_end].strip()
            elif '```' in response_text:
                json_start = response_text.find('```') + 3
                json_end = response_text.find('```', json_start)
                json_text = response_text[json_start:json_end].strip()
            else:
                # Try to find JSON object
                json_start = response_text.find('{')
                json_end = response_text.rfind('}') + 1
                json_text = response_text[json_start:json_end]
            
            analysis = json.loads(json_text)
            
            # Validate required fields
            required_fields = ['fraud_probability', 'confidence', 'reasoning', 'red_flags', 'recommendation']
            for field in required_fields:
                if field not in analysis:
                    raise ValueError(f"Missing required field: {field}")
            
            # Ensure lists
            if not isinstance(analysis.get('red_flags'), list):
                analysis['red_flags'] = []
            if not isinstance(analysis.get('green_flags'), list):
                analysis['green_flags'] = []
            
            # Clamp values between 0 and 1
            analysis['fraud_probability'] = max(0.0, min(1.0, float(analysis['fraud_probability'])))
            analysis['confidence'] = max(0.0, min(1.0, float(analysis['confidence'])))
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error parsing Gemini response: {e}")
            logger.debug(f"Response text: {response_text[:500]}")
            
            # Return default analysis
            return {
                'fraud_probability': 0.5,
                'confidence': 0.3,
                'reasoning': f"Could not parse AI response. Error: {str(e)}",
                'red_flags': ['AI analysis failed'],
                'green_flags': [],
                'recommendation': 'PROCEED WITH CAUTION'
            }
    
    def _fallback_analysis(self, job_data: Dict) -> Dict:
        """Fallback rule-based analysis when LLM is not available"""
        return {
            'fraud_probability': 0.5,
            'confidence': 0.5,
            'reasoning': 'LLM analysis not available - using rule-based detection',
            'red_flags': [],
            'green_flags': [],
            'recommendation': 'PROCEED WITH CAUTION'
        }

# Singleton instance
_llm_analyzer = None

def get_llm_analyzer():
    """Get or create LLM analyzer instance"""
    global _llm_analyzer
    if _llm_analyzer is None:
        _llm_analyzer = LLMFraudAnalyzer()
    return _llm_analyzer
