"""
API Routes for TrustHire with Enhanced LLM Fraud Detection
"""

from flask import Blueprint, request, jsonify
from database import db, Job, UserReport, SearchHistory
from models.job_model import JobAggregator
from models.fraud_detector import get_fraud_detector
from utils.validators import Validators
import logging

logger = logging.getLogger(__name__)

api = Blueprint('api', __name__, url_prefix='/api')

# Initialize job aggregator and fraud detector
job_aggregator = JobAggregator()
fraud_detector = get_fraud_detector()

@api.route('/search', methods=['POST'])
def search_jobs():
    """
    Search for jobs across platforms with keyword-based scraping
    Body: {query, location, experience, platforms, save_to_db}
    """
    try:
        data = request.get_json()
        
        # Validate input
        query = data.get('query', '').strip()
        if not Validators.validate_query(query):
            return jsonify({'error': 'Invalid query. Must be 2-200 characters.'}), 400
        
        location = data.get('location', '').strip()
        if not Validators.validate_location(location):
            return jsonify({'error': 'Invalid location'}), 400
        
        experience = data.get('experience', '').strip()
        if not Validators.validate_experience(experience):
            return jsonify({'error': 'Invalid experience level'}), 400
        
        platforms = data.get('platforms', ['all'])
        if not isinstance(platforms, list):
            platforms = [platforms]
        
        # Available platforms - scraper-friendly sources that work well
        # RemoteOK and Remotive - Both work perfectly with APIs
        # WeWorkRemotely is blocked by Cloudflare (403)
        available_platforms = ['remoteok', 'remotive']
        
        # If 'all' is selected or platforms list is empty, use all available platforms
        if 'all' in platforms or not platforms:
            selected_platforms = available_platforms
        else:
            # Filter valid platforms
            selected_platforms = [p for p in platforms if p in available_platforms]
            if not selected_platforms:
                selected_platforms = available_platforms
        
        # Sanitize inputs
        query = Validators.sanitize_input(query)
        location = Validators.sanitize_input(location)
        
        # Search jobs with dynamic keyword-based scraping
        logger.info(f"🔍 Searching for keyword: '{query}' | Location: '{location}' | Experience: '{experience}'")
        logger.info(f"📊 Platforms: {selected_platforms}")
        
        jobs = job_aggregator.search_all_platforms(
            query=query,
            location=location,
            experience=experience,
            platforms=selected_platforms
        )
        
        # Enhance with LLM fraud detection
        logger.info(f"🤖 Running LLM fraud detection on {len(jobs)} jobs...")
        enhanced_jobs = []
        
        for job in jobs:
            try:
                # Run comprehensive fraud detection with timeout protection
                fraud_analysis = fraud_detector.predict(job)
                
                # Merge fraud analysis into job data
                job['trust_score'] = fraud_analysis['trust_score']
                job['is_fraudulent'] = fraud_analysis['is_fraudulent']
                job['fraud_confidence'] = fraud_analysis['fraud_confidence']
                job['fraud_signals'] = fraud_analysis['fraud_signals']
                job['fraud_reasons'] = fraud_analysis['detailed_reasons']
                job['company_verification'] = fraud_analysis['company_verification']
                job['job_availability'] = fraud_analysis['job_availability']
                job['final_verdict'] = fraud_analysis['final_verdict']
                
                # Add verification badges
                if job.get('verified_source'):
                    job['verification_badge'] = '✅ VERIFIED OFFICIAL SOURCE'
                elif fraud_analysis['company_verification'].get('is_real'):
                    job['verification_badge'] = '✓ Company Verified'
                else:
                    job['verification_badge'] = '⚠️ Unverified'
                    
            except Exception as e:
                logger.error(f"Error analyzing job {job.get('title')}: {e}")
                # Provide default values if fraud detection fails
                job['trust_score'] = 0.5
                job['is_fraudulent'] = False
                job['fraud_confidence'] = 0.0
                job['fraud_signals'] = []
                job['fraud_reasons'] = ['Analysis unavailable']
                job['company_verification'] = {'is_real': False, 'confidence': 0.0}
                job['job_availability'] = {'is_available': None}
                job['final_verdict'] = '⚠️ Analysis pending'
                job['verification_badge'] = '⚠️ Unverified'
            
            enhanced_jobs.append(job)
        
        # Sort by trust score (highest first)
        enhanced_jobs.sort(key=lambda x: x['trust_score'], reverse=True)
        
        # Track search
        job_aggregator.track_search(query, location, experience)
        
        # Optionally save to database
        if data.get('save_to_db', False):
            saved = job_aggregator.save_jobs_to_db(enhanced_jobs)
            logger.info(f"💾 Saved {saved} new jobs to database")
        
        # Generate summary statistics
        total_jobs = len(enhanced_jobs)
        trusted_jobs = len([j for j in enhanced_jobs if j['trust_score'] >= 0.7])
        verified_companies = len([j for j in enhanced_jobs if j['company_verification'].get('is_real')])
        active_jobs = len([j for j in enhanced_jobs if j.get('job_availability', {}).get('is_available') == True])
        
        logger.info(f"✅ Search complete: {total_jobs} jobs | {trusted_jobs} trusted | {verified_companies} verified companies | {active_jobs} active")
        
        return jsonify({
            'success': True,
            'count': total_jobs,
            'jobs': enhanced_jobs,
            'query': query,
            'location': location,
            'experience': experience,
            'summary': {
                'total_jobs': total_jobs,
                'trusted_jobs': trusted_jobs,
                'verified_companies': verified_companies,
                'active_jobs': active_jobs,
                'fraud_detected': total_jobs - trusted_jobs
            }
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Error in search endpoint: {e}", exc_info=True)
        return jsonify({'error': 'Internal server error', 'message': str(e)}), 500

@api.route('/jobs/<int:job_id>/analyze', methods=['GET'])
def analyze_job(job_id):
    """
    Deep analysis of a specific job with real-time fraud detection
    """
    try:
        job = Job.query.get(job_id)
        if not job:
            return jsonify({'error': 'Job not found'}), 404
        
        # Convert to dict
        job_data = job.to_dict()
        
        # Run comprehensive fraud analysis
        logger.info(f"🔍 Running deep fraud analysis on job: {job_data.get('title')} at {job_data.get('company')}")
        fraud_analysis = fraud_detector.predict(job_data)
        
        # Build detailed analysis response
        analysis_result = {
            'job': job_data,
            'fraud_detection': {
                'trust_score': fraud_analysis['trust_score'],
                'trust_percentage': f"{fraud_analysis['trust_score'] * 100:.1f}%",
                'is_fraudulent': fraud_analysis['is_fraudulent'],
                'fraud_confidence': fraud_analysis['fraud_confidence'],
                'verdict': fraud_analysis['final_verdict'],
                'recommendation': _get_recommendation(fraud_analysis['trust_score'])
            },
            'company_verification': {
                'is_verified': fraud_analysis['company_verification'].get('is_real', False),
                'confidence': fraud_analysis['company_verification'].get('confidence', 0),
                'confidence_percentage': f"{fraud_analysis['company_verification'].get('confidence', 0) * 100:.0f}%",
                'reason': fraud_analysis['company_verification'].get('reason', ''),
                'sources': fraud_analysis['company_verification'].get('sources_found', []),
                'reviews': fraud_analysis['company_verification'].get('reviews', {}),
                'online_presence': fraud_analysis['company_verification'].get('online_presence', {})
            },
            'job_availability': {
                'is_available': fraud_analysis['job_availability'].get('is_available'),
                'status': fraud_analysis['job_availability'].get('reason', ''),
                'status_code': fraud_analysis['job_availability'].get('status_code', 0)
            },
            'fraud_signals': fraud_analysis['fraud_signals'],
            'detailed_reasons': fraud_analysis['detailed_reasons'],
            'llm_analysis': fraud_analysis.get('llm_analysis', {})
        }
        
        return jsonify({
            'success': True,
            'analysis': analysis_result
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Error in analyze_job endpoint: {e}", exc_info=True)
        return jsonify({'error': 'Internal server error', 'message': str(e)}), 500

@api.route('/verify-company', methods=['POST'])
def verify_company():
    """
    Verify a company online with real-time checks
    Body: {company_name}
    """
    try:
        data = request.get_json()
        company_name = data.get('company_name', '').strip()
        
        if not company_name or len(company_name) < 3:
            return jsonify({'error': 'Invalid company name'}), 400
        
        logger.info(f"🔍 Verifying company: {company_name}")
        
        # Run company verification
        verification = fraud_detector.verify_company_online(company_name)
        
        return jsonify({
            'success': True,
            'company': company_name,
            'verification': verification
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Error in verify_company endpoint: {e}", exc_info=True)
        return jsonify({'error': 'Internal server error'}), 500

@api.route('/check-job-availability', methods=['POST'])
def check_job_availability():
    """
    Check if a job is still available by visiting the URL
    Body: {job_url}
    """
    try:
        data = request.get_json()
        job_url = data.get('job_url', '').strip()
        
        if not job_url:
            return jsonify({'error': 'Job URL is required'}), 400
        
        logger.info(f"🔗 Checking job availability: {job_url}")
        
        # Check availability
        availability = fraud_detector.check_job_availability(job_url)
        
        return jsonify({
            'success': True,
            'url': job_url,
            'availability': availability
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Error in check_job_availability endpoint: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@api.route('/jobs', methods=['GET'])
def get_jobs():
    """
    Get jobs from database with filters
    Query params: platform, location, min_trust_score, page, per_page
    """
    try:
        platform = request.args.get('platform', '')
        location = request.args.get('location', '')
        min_trust_score = float(request.args.get('min_trust_score', 0.4))
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        
        # Build query
        query = Job.query.filter(Job.is_active == True)
        
        if platform and platform != 'all':
            query = query.filter(Job.platform == platform)
        
        if location:
            query = query.filter(Job.location.ilike(f'%{location}%'))
        
        query = query.filter(Job.trust_score >= min_trust_score)
        
        # Sort by trust score
        query = query.order_by(Job.trust_score.desc(), Job.scraped_at.desc())
        
        # Paginate
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        
        jobs = [job.to_dict() for job in pagination.items]
        
        return jsonify({
            'success': True,
            'jobs': jobs,
            'total': pagination.total,
            'page': page,
            'per_page': per_page,
            'pages': pagination.pages
        }), 200
        
    except Exception as e:
        logger.error(f"Error in get_jobs endpoint: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@api.route('/jobs/<int:job_id>', methods=['GET'])
def get_job(job_id):
    """Get single job details with fraud analysis"""
    try:
        job = Job.query.get(job_id)
        if not job:
            return jsonify({'error': 'Job not found'}), 404
        
        # Increment view count
        job.views += 1
        db.session.commit()
        
        job_data = job.to_dict()
        
        # Add real-time fraud analysis
        fraud_analysis = fraud_detector.predict(job_data)
        job_data['fraud_analysis'] = {
            'trust_score': fraud_analysis['trust_score'],
            'verdict': fraud_analysis['final_verdict'],
            'company_verified': fraud_analysis['company_verification'].get('is_real', False),
            'job_available': fraud_analysis['job_availability'].get('is_available')
        }
        
        return jsonify({
            'success': True,
            'job': job_data
        }), 200
        
    except Exception as e:
        logger.error(f"Error in get_job endpoint: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@api.route('/jobs/<int:job_id>/report', methods=['POST'])
def report_job(job_id):
    """Report a job as fraudulent"""
    try:
        data = request.get_json()
        reason = data.get('reason', '').strip()
        
        if not reason or len(reason) < 10:
            return jsonify({'error': 'Please provide a detailed reason (min 10 characters)'}), 400
        
        job = Job.query.get(job_id)
        if not job:
            return jsonify({'error': 'Job not found'}), 404
        
        # Create report
        report = UserReport(
            job_id=job_id,
            reason=reason
        )
        db.session.add(report)
        
        # Increment report count
        job.reports += 1
        
        # If multiple reports, lower trust score
        if job.reports >= 3:
            job.trust_score = max(0.1, job.trust_score - 0.2)
            job.is_fraudulent = True
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Report submitted successfully'
        }), 200
        
    except Exception as e:
        logger.error(f"Error in report_job endpoint: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@api.route('/stats', methods=['GET'])
def get_stats():
    """Get platform statistics with fraud insights"""
    try:
        total_jobs = Job.query.count()
        active_jobs = Job.query.filter(Job.is_active == True).count()
        fraudulent_jobs = Job.query.filter(Job.is_fraudulent == True).count()
        trusted_jobs = Job.query.filter(Job.trust_score >= 0.7).count()
        
        # Platform breakdown
        platform_stats = db.session.query(
            Job.platform, 
            db.func.count(Job.id)
        ).group_by(Job.platform).all()
        
        # Popular searches - handle if table is empty
        try:
            popular_searches = SearchHistory.query.order_by(
                SearchHistory.count.desc()
            ).limit(10).all()
            popular_searches_list = [
                {'query': s.query, 'count': s.count} 
                for s in popular_searches
            ]
        except Exception as search_error:
            logger.warning(f"Could not fetch search history: {search_error}")
            popular_searches_list = []
        
        return jsonify({
            'success': True,
            'stats': {
                'total_jobs': total_jobs,
                'active_jobs': active_jobs,
                'trusted_jobs': trusted_jobs,
                'fraudulent_jobs': fraudulent_jobs,
                'fraud_rate': round(fraudulent_jobs / total_jobs * 100, 2) if total_jobs > 0 else 0,
                'trust_rate': round(trusted_jobs / total_jobs * 100, 2) if total_jobs > 0 else 0,
                'platforms': {platform: count for platform, count in platform_stats},
                'popular_searches': popular_searches_list
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error in stats endpoint: {e}", exc_info=True)
        return jsonify({'error': 'Internal server error', 'message': str(e)}), 500

@api.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'TrustHire API'
    }), 200

def _get_recommendation(trust_score: float) -> str:
    """Generate application recommendation based on trust score"""
    if trust_score >= 0.85:
        return "✅ HIGHLY RECOMMENDED - This job appears safe to apply. Company is verified and job details look legitimate."
    elif trust_score >= 0.7:
        return "✅ RECOMMENDED - This job looks trustworthy. Company verified with good indicators."
    elif trust_score >= 0.5:
        return "⚠️ PROCEED WITH CAUTION - Verify company details independently before applying. Some concerns detected."
    elif trust_score >= 0.3:
        return "⚠️ HIGH CAUTION - Multiple red flags detected. Research thoroughly before considering."
    else:
        return "❌ NOT RECOMMENDED - High likelihood of fraud. Do NOT apply or share personal information."
