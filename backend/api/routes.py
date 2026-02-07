"""
API Routes for TrustHire
"""

from flask import Blueprint, request, jsonify
from database import db, Job, UserReport, SearchHistory
from models.job_model import JobAggregator
from utils.validators import Validators
import logging

logger = logging.getLogger(__name__)

api = Blueprint('api', __name__, url_prefix='/api')

# Initialize job aggregator
job_aggregator = JobAggregator()

@api.route('/search', methods=['POST'])
def search_jobs():
    """
    Search for jobs across platforms
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
        
        # Sanitize inputs
        query = Validators.sanitize_input(query)
        location = Validators.sanitize_input(location)
        
        # Search jobs
        logger.info(f"Searching for '{query}' in '{location}' with experience '{experience}'")
        jobs = job_aggregator.search_all_platforms(
            query=query,
            location=location,
            experience=experience,
            platforms=platforms
        )
        
        # Track search
        job_aggregator.track_search(query, location, experience)
        
        # Optionally save to database
        if data.get('save_to_db', False):
            saved = job_aggregator.save_jobs_to_db(jobs)
            logger.info(f"Saved {saved} new jobs to database")
        
        return jsonify({
            'success': True,
            'count': len(jobs),
            'jobs': jobs,
            'query': query,
            'location': location,
            'experience': experience
        }), 200
        
    except Exception as e:
        logger.error(f"Error in search endpoint: {e}")
        return jsonify({'error': 'Internal server error', 'message': str(e)}), 500

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
    """Get single job details"""
    try:
        job = Job.query.get(job_id)
        if not job:
            return jsonify({'error': 'Job not found'}), 404
        
        # Increment view count
        job.views += 1
        db.session.commit()
        
        return jsonify({
            'success': True,
            'job': job.to_dict()
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
    """Get platform statistics"""
    try:
        total_jobs = Job.query.count()
        active_jobs = Job.query.filter(Job.is_active == True).count()
        fraudulent_jobs = Job.query.filter(Job.is_fraudulent == True).count()
        
        # Platform breakdown
        platform_stats = db.session.query(
            Job.platform, 
            db.func.count(Job.id)
        ).group_by(Job.platform).all()
        
        # Popular searches
        popular_searches = SearchHistory.query.order_by(
            SearchHistory.count.desc()
        ).limit(10).all()
        
        return jsonify({
            'success': True,
            'stats': {
                'total_jobs': total_jobs,
                'active_jobs': active_jobs,
                'fraudulent_jobs': fraudulent_jobs,
                'fraud_rate': round(fraudulent_jobs / total_jobs * 100, 2) if total_jobs > 0 else 0,
                'platforms': {platform: count for platform, count in platform_stats},
                'popular_searches': [
                    {'query': s.query, 'count': s.count} 
                    for s in popular_searches
                ]
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error in stats endpoint: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@api.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'TrustHire API'
    }), 200
