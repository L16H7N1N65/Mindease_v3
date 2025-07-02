"""
Flask integration for ETL pipeline.
"""
import logging
from flask import Blueprint, jsonify, current_app
from flask_jwt_extended import jwt_required

from app.db.session import SessionLocal
from app.etl.run_etl import run_etl
from app.core.dependencies import get_current_admin_user

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create blueprint
etl_blueprint = Blueprint('etl', __name__, url_prefix='/api/v1/etl')


@etl_blueprint.route('/run', methods=['POST'])
@jwt_required()
@get_current_admin_user
def trigger_etl():
    """
    Trigger ETL process.
    
    - Requires admin privileges
    - Processes all datasets in the archive folder
    - Returns summary of processed documents
    """
    try:
        # Get database session
        db = SessionLocal()
        
        # Run ETL process
        run_etl(db)
        
        return jsonify({
            "status": "success",
            "message": "ETL process completed successfully"
        }), 200
    
    except Exception as e:
        logger.error(f"Error running ETL process: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"Error running ETL process: {str(e)}"
        }), 500


@etl_blueprint.route('/status', methods=['GET'])
@jwt_required()
@get_current_admin_user
def etl_status():
    """
    Get ETL status.
    
    - Requires admin privileges
    - Returns status of ETL process
    """
    # In a real application, this would check the status of any running ETL processes
    # For now, we'll just return a placeholder
    return jsonify({
        "status": "idle",
        "last_run": None,
        "next_scheduled_run": None
    }), 200


def register_etl_blueprint(app):
    """
    Register ETL blueprint with Flask application.
    
    Args:
        app: Flask application
    """
    app.register_blueprint(etl_blueprint)
    
    # Schedule ETL process to run at application startup if configured
    if app.config.get('RUN_ETL_ON_STARTUP', False):
        @app.before_first_request
        def run_etl_on_startup():
            try:
                db = SessionLocal()
                run_etl(db)
                logger.info("ETL process completed on application startup")
            except Exception as e:
                logger.error(f"Error running ETL process on startup: {str(e)}")
