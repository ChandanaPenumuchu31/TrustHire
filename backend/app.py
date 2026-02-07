"""
TrustHire - Job Aggregation Platform with Fraud Detection
Main Flask Application
"""

from flask import Flask, jsonify
from flask_cors import CORS
from config import Config
from database import init_db
from api.routes import api
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_app():
    """Application factory"""
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Enable CORS
    CORS(app, resources={r"/api/*": {"origins": Config.CORS_ORIGINS}})
    
    # Initialize database
    init_db(app)
    
    # Register blueprints
    app.register_blueprint(api)
    
    # Root endpoint
    @app.route('/')
    def index():
        return jsonify({
            'service': 'TrustHire API',
            'version': '1.0.0',
            'description': 'Job aggregation platform with AI-powered fraud detection',
            'endpoints': {
                'search': '/api/search',
                'jobs': '/api/jobs',
                'job_details': '/api/jobs/<id>',
                'report_fraud': '/api/jobs/<id>/report',
                'statistics': '/api/stats',
                'health': '/api/health'
            },
            'features': [
                'Multi-platform job scraping (LinkedIn, Indeed, Naukri)',
                'AI/ML fraud detection',
                'Trust score for each job',
                'Community fraud reporting',
                'Advanced filtering and search'
            ]
        })
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Endpoint not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"Internal error: {error}")
        return jsonify({'error': 'Internal server error'}), 500
    
    logger.info("TrustHire API initialized successfully")
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=Config.DEBUG
    )
