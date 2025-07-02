"""
RAG Learning Router

API endpoints for managing RAG system learning and continuous improvement.
"""
import logging
from typing import Dict, List, Optional, Any
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session

from app.core.dependencies import get_db, get_current_admin_user
from app.db.models.auth import User
from app.services.rag_learning_service import RAGLearningService
from app.services.rag_learning_framework import LearningMethod, LearningConfig
from app.schemas.rag_learning import (
    LearningReadinessResponse,
    ExperimentCreateRequest,
    ExperimentResponse,
    ExperimentListResponse,
    LearningRecommendationsResponse
)

logger = logging.getLogger(__name__)

# router = APIRouter(prefix="/rag/learning", tags=["RAG Learning"])
router = APIRouter(tags=[("rag/learning")])



@router.get("/readiness", response_model=LearningReadinessResponse)
async def assess_learning_readiness(
    organization_id: Optional[str] = None,
    min_samples: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Assess whether the RAG system has sufficient data for learning.
    
    This endpoint evaluates:
    - Data quantity and quality
    - Safety concerns
    - Feedback completeness
    - Recommended learning approach
    """
    
    try:
        service = RAGLearningService(db)
        
        # Use user's organization if not specified
        if organization_id is None:
            organization_id = current_user.organization_id
        
        readiness = await service.assess_learning_readiness(organization_id, min_samples)
        
        logger.info(f"Learning readiness assessed for org {organization_id}: {readiness['readiness_status']}")
        return readiness
        
    except Exception as e:
        logger.error(f"Error assessing learning readiness: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/experiments", response_model=ExperimentResponse)
async def start_learning_experiment(
    request: ExperimentCreateRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Start a new RAG learning experiment.
    
    This will:
    1. Assess data readiness
    2. Prepare training data from user feedback
    3. Select appropriate learning method
    4. Start training process
    """
    
    try:
        service = RAGLearningService(db)
        
        # Use user's organization if not specified
        organization_id = request.organization_id or current_user.organization_id
        
        # Convert string method to enum if provided
        method = LearningMethod(request.method) if request.method else None
        
        # Start experiment
        experiment_id = await service.start_learning_experiment(
            organization_id=organization_id,
            method=method,
            config=request.config
        )
        
        logger.info(f"Started learning experiment {experiment_id} for org {organization_id}")
        
        return {
            "experiment_id": experiment_id,
            "status": "started",
            "organization_id": organization_id,
            "method": method.value if method else "auto_selected",
            "message": "Learning experiment started successfully"
        }
        
    except ValueError as e:
        logger.warning(f"Invalid request for learning experiment: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error starting learning experiment: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/experiments", response_model=ExperimentListResponse)
async def list_experiments(
    organization_id: Optional[str] = None,
    status_filter: Optional[str] = None,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    List learning experiments with optional filtering.
    """
    
    try:
        service = RAGLearningService(db)
        
        # Use user's organization if not specified
        if organization_id is None:
            organization_id = current_user.organization_id
        
        experiments = await service.list_experiments(organization_id, status_filter)
        
        # Apply limit
        experiments = experiments[:limit]
        
        return {
            "experiments": experiments,
            "total": len(experiments),
            "organization_id": organization_id,
            "status_filter": status_filter
        }
        
    except Exception as e:
        logger.error(f"Error listing experiments: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/experiments/{experiment_id}", response_model=ExperimentResponse)
async def get_experiment_status(
    experiment_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Get the status and details of a specific learning experiment.
    """
    
    try:
        service = RAGLearningService(db)
        status = await service.get_experiment_status(experiment_id)
        
        if status.get("status") == "not_found":
            raise HTTPException(status_code=404, detail="Experiment not found")
        
        return status
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting experiment status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/experiments/{experiment_id}/evaluate")
async def evaluate_experiment(
    experiment_id: str,
    background_tasks: BackgroundTasks,
    organization_id: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Evaluate a completed learning experiment.
    
    This will test the trained model on recent data and provide
    performance metrics compared to the baseline.
    """
    
    try:
        service = RAGLearningService(db)
        
        # Use user's organization if not specified
        if organization_id is None:
            organization_id = current_user.organization_id
        
        # Start evaluation in background
        background_tasks.add_task(
            service.evaluate_experiment,
            experiment_id,
            organization_id
        )
        
        return {
            "experiment_id": experiment_id,
            "status": "evaluation_started",
            "message": "Model evaluation started. Check status for results."
        }
        
    except Exception as e:
        logger.error(f"Error starting experiment evaluation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/experiments/{experiment_id}/deploy")
async def deploy_experiment(
    experiment_id: str,
    deployment_config: Optional[Dict[str, Any]] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Deploy a trained and evaluated model to production.
    
    This will replace the current RAG model with the improved version
    after safety and performance validation.
    """
    
    try:
        service = RAGLearningService(db)
        
        model_path = await service.deploy_experiment(experiment_id, deployment_config)
        
        logger.info(f"Deployed experiment {experiment_id} to {model_path}")
        
        return {
            "experiment_id": experiment_id,
            "status": "deployed",
            "model_path": model_path,
            "message": "Model deployed successfully to production"
        }
        
    except ValueError as e:
        logger.warning(f"Invalid deployment request: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error deploying experiment: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/recommendations", response_model=LearningRecommendationsResponse)
async def get_learning_recommendations(
    organization_id: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Get personalized recommendations for improving the RAG system.
    
    This provides actionable insights on:
    - Data collection strategies
    - Appropriate learning methods
    - Performance improvement opportunities
    - Safety and quality enhancements
    """
    
    try:
        service = RAGLearningService(db)
        
        # Use user's organization if not specified
        if organization_id is None:
            organization_id = current_user.organization_id
        
        recommendations = await service.get_learning_recommendations(organization_id)
        
        return recommendations
        
    except Exception as e:
        logger.error(f"Error getting learning recommendations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/methods")
async def list_learning_methods():
    """
    List available learning methods with descriptions.
    """
    
    methods = {
        "supervised_fine_tuning": {
            "name": "Supervised Fine-Tuning",
            "description": "Traditional fine-tuning with labeled examples",
            "best_for": "Large datasets with high-quality labels",
            "data_requirements": "500+ high-quality examples",
            "training_time": "Medium (2-4 hours)",
            "resource_requirements": "High"
        },
        "parameter_efficient_fine_tuning": {
            "name": "Parameter Efficient Fine-Tuning (LoRA)",
            "description": "Efficient fine-tuning using Low-Rank Adaptation",
            "best_for": "Limited data or computational resources",
            "data_requirements": "100+ examples",
            "training_time": "Fast (30-60 minutes)",
            "resource_requirements": "Low"
        },
        "reinforcement_learning": {
            "name": "Reinforcement Learning",
            "description": "Learning from user interactions and feedback",
            "best_for": "Interactive feedback and preference data",
            "data_requirements": "Continuous feedback stream",
            "training_time": "Long (4-8 hours)",
            "resource_requirements": "High"
        },
        "retrieval_augmented_fine_tuning": {
            "name": "Retrieval Augmented Fine-Tuning (RAFT)",
            "description": "Specialized training for retrieval-augmented generation",
            "best_for": "Improving document retrieval and relevance",
            "data_requirements": "300+ query-document pairs",
            "training_time": "Medium (1-3 hours)",
            "resource_requirements": "Medium"
        },
        "direct_preference_optimization": {
            "name": "Direct Preference Optimization",
            "description": "Training on human preferences without reward modeling",
            "best_for": "Comparative feedback and preference data",
            "data_requirements": "200+ preference pairs",
            "training_time": "Medium (1-2 hours)",
            "resource_requirements": "Medium"
        },
        "constitutional_ai": {
            "name": "Constitutional AI",
            "description": "Training for safety and ethical behavior",
            "best_for": "Addressing safety concerns and harmful outputs",
            "data_requirements": "Safety-focused feedback",
            "training_time": "Medium (2-3 hours)",
            "resource_requirements": "Medium"
        }
    }
    
    return {
        "methods": methods,
        "selection_guidance": {
            "limited_data": "parameter_efficient_fine_tuning",
            "safety_concerns": "constitutional_ai",
            "preference_data": "direct_preference_optimization",
            "retrieval_issues": "retrieval_augmented_fine_tuning",
            "interactive_feedback": "reinforcement_learning",
            "default": "supervised_fine_tuning"
        }
    }


@router.get("/training-data/stats")
async def get_training_data_stats(
    organization_id: Optional[str] = None,
    days: int = 30,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Get statistics about available training data.
    """
    
    try:
        service = RAGLearningService(db)
        
        # Use user's organization if not specified
        if organization_id is None:
            organization_id = current_user.organization_id
        
        # Get training data
        training_data = await service.prepare_training_data(
            organization_id=organization_id,
            days=days,
            min_quality_score=0.0  # Include all data for stats
        )
        
        # Calculate statistics
        total_samples = len(training_data)
        high_quality = len([d for d in training_data if d.feedback_score >= 0.8])
        medium_quality = len([d for d in training_data if 0.6 <= d.feedback_score < 0.8])
        low_quality = len([d for d in training_data if d.feedback_score < 0.6])
        
        safety_issues = len([d for d in training_data if d.safety_score < 0.9])
        with_suggestions = len([d for d in training_data if d.improvement_suggestions])
        
        # Quality distribution
        quality_distribution = {
            "high": high_quality,
            "medium": medium_quality,
            "low": low_quality
        }
        
        # Intent distribution
        intent_counts = {}
        for data in training_data:
            intent = data.context_metadata.get("query_intent", "unknown")
            intent_counts[intent] = intent_counts.get(intent, 0) + 1
        
        return {
            "total_samples": total_samples,
            "quality_distribution": quality_distribution,
            "safety_issues": safety_issues,
            "with_suggestions": with_suggestions,
            "intent_distribution": intent_counts,
            "data_period_days": days,
            "organization_id": organization_id,
            "readiness_assessment": {
                "sufficient_data": total_samples >= 100,
                "good_quality_ratio": high_quality / total_samples if total_samples > 0 else 0,
                "safety_concern_ratio": safety_issues / total_samples if total_samples > 0 else 0,
                "ready_for_learning": total_samples >= 100 and safety_issues / total_samples < 0.1 if total_samples > 0 else False
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting training data stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/experiments/{experiment_id}")
async def delete_experiment(
    experiment_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Delete a learning experiment and its associated files.
    
    This is irreversible and will remove all experiment data.
    """
    
    try:
        service = RAGLearningService(db)
        
        # Check if experiment exists
        status = await service.get_experiment_status(experiment_id)
        if status.get("status") == "not_found":
            raise HTTPException(status_code=404, detail="Experiment not found")
        
        # Prevent deletion of deployed models
        if status.get("status") == "deployed":
            raise HTTPException(
                status_code=400,
                detail="Cannot delete deployed experiment. Undeploy first."
            )
        
        # Delete experiment files
        import shutil
        from pathlib import Path
        
        experiment_dir = Path("experiments") / experiment_id
        if experiment_dir.exists():
            shutil.rmtree(experiment_dir)
        
        logger.info(f"Deleted experiment {experiment_id}")
        
        return {
            "experiment_id": experiment_id,
            "status": "deleted",
            "message": "Experiment deleted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting experiment: {e}")
        raise HTTPException(status_code=500, detail=str(e))

