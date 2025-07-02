"""
RAG Learning Service

Service layer for managing continuous learning and improvement
of the RAG system using various machine learning approaches.
"""
import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from app.db.models.rag_feedback import RAGFeedback, FeedbackTrainingData
from app.services.rag_learning_framework import (
    RAGLearningFramework, LearningMethod, LearningConfig, TrainingData
)

logger = logging.getLogger(__name__)


class RAGLearningService:
    """
    Service for managing RAG system learning and improvement.
    
    This service orchestrates the continuous learning process by:
    1. Collecting and preparing training data from user feedback
    2. Selecting appropriate learning methods
    3. Managing training experiments
    4. Evaluating and deploying improved models
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.learning_framework = RAGLearningFramework()
        
    async def assess_learning_readiness(
        self,
        organization_id: Optional[str] = None,
        min_samples: int = 100
    ) -> Dict[str, Any]:
        """
        Assess whether the system has enough quality data for learning.
        
        Returns:
            Assessment of data readiness and recommended learning approach
        """
        
        # Get recent feedback data
        query = self.db.query(RAGFeedback)\
            .filter(RAGFeedback.created_at >= datetime.utcnow() - timedelta(days=30))
        
        if organization_id:
            from app.db.models.auth import User
            query = query.join(User).filter(User.organization_id == organization_id)
        
        feedback_records = query.all()
        
        # Analyze data quality and quantity
        total_samples = len(feedback_records)
        quality_samples = len([f for f in feedback_records if f.overall_rating and f.overall_rating >= 4])
        safety_issues = len([f for f in feedback_records if f.is_safe is False])
        detailed_feedback = len([f for f in feedback_records if f.feedback_text])
        
        # Calculate readiness metrics
        data_sufficiency = min(total_samples / min_samples, 1.0)
        quality_ratio = quality_samples / total_samples if total_samples > 0 else 0
        safety_concern_ratio = safety_issues / total_samples if total_samples > 0 else 0
        feedback_detail_ratio = detailed_feedback / total_samples if total_samples > 0 else 0
        
        # Determine readiness status
        if total_samples < min_samples:
            readiness_status = "insufficient_data"
            recommended_action = "collect_more_feedback"
        elif safety_concern_ratio > 0.1:
            readiness_status = "safety_concerns"
            recommended_action = "address_safety_first"
        elif quality_ratio < 0.6:
            readiness_status = "low_quality_data"
            recommended_action = "improve_data_quality"
        else:
            readiness_status = "ready"
            recommended_action = "start_learning"
        
        # Recommend learning method
        if readiness_status == "ready":
            if total_samples < 500:
                recommended_method = LearningMethod.PARAMETER_EFFICIENT_FINE_TUNING
            elif safety_concern_ratio > 0.05:
                recommended_method = LearningMethod.CONSTITUTIONAL_AI
            elif feedback_detail_ratio > 0.7:
                recommended_method = LearningMethod.DIRECT_PREFERENCE_OPTIMIZATION
            else:
                recommended_method = LearningMethod.SUPERVISED_FINE_TUNING
        else:
            recommended_method = None
        
        return {
            "readiness_status": readiness_status,
            "recommended_action": recommended_action,
            "recommended_method": recommended_method.value if recommended_method else None,
            "data_metrics": {
                "total_samples": total_samples,
                "quality_samples": quality_samples,
                "safety_issues": safety_issues,
                "detailed_feedback": detailed_feedback,
                "data_sufficiency": data_sufficiency,
                "quality_ratio": quality_ratio,
                "safety_concern_ratio": safety_concern_ratio,
                "feedback_detail_ratio": feedback_detail_ratio
            },
            "recommendations": self._get_improvement_recommendations(
                readiness_status, quality_ratio, safety_concern_ratio, feedback_detail_ratio
            )
        }
    
    async def prepare_training_data(
        self,
        organization_id: Optional[str] = None,
        days: int = 30,
        min_quality_score: float = 0.7
    ) -> List[TrainingData]:
        """
        Prepare training data from user feedback.
        
        Args:
            organization_id: Filter by organization
            days: Number of days of feedback to include
            min_quality_score: Minimum quality threshold for inclusion
            
        Returns:
            List of TrainingData objects ready for ML training
        """
        
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Get feedback with sufficient quality
        query = self.db.query(RAGFeedback)\
            .filter(
                RAGFeedback.created_at >= start_date,
                RAGFeedback.overall_rating.isnot(None)
            )
        
        if organization_id:
            from app.db.models.auth import User
            query = query.join(User).filter(User.organization_id == organization_id)
        
        feedback_records = query.all()
        
        # Convert to TrainingData format
        training_data = []
        for feedback in feedback_records:
            # Calculate quality score
            quality_score = self._calculate_quality_score(feedback)
            
            if quality_score >= min_quality_score:
                training_data.append(TrainingData(
                    query=feedback.user_query,
                    response=feedback.rag_response,
                    retrieved_docs=feedback.retrieved_documents or [],
                    feedback_score=feedback.overall_rating / 5.0,  # Normalize to 0-1
                    safety_score=1.0 if feedback.is_safe is True else 0.5 if feedback.is_safe is None else 0.0,
                    relevance_score=feedback.relevance_score / 5.0 if feedback.relevance_score else 0.5,
                    quality_label=self._get_quality_label(feedback.overall_rating),
                    improvement_suggestions=self._extract_suggestions(feedback),
                    context_metadata={
                        "query_intent": feedback.query_intent,
                        "emotional_state": feedback.user_emotional_state,
                        "conversation_id": str(feedback.conversation_id) if feedback.conversation_id else None,
                        "feedback_category": feedback.feedback_category,
                        "session_context": feedback.session_context or {}
                    }
                ))
        
        logger.info(f"Prepared {len(training_data)} training samples from {len(feedback_records)} feedback records")
        return training_data
    
    async def start_learning_experiment(
        self,
        organization_id: Optional[str] = None,
        method: Optional[LearningMethod] = None,
        config: Optional[LearningConfig] = None
    ) -> str:
        """
        Start a new learning experiment.
        
        Args:
            organization_id: Organization to train for
            method: Specific learning method to use
            config: Custom learning configuration
            
        Returns:
            experiment_id: Unique identifier for the experiment
        """
        
        # Assess readiness
        readiness = await self.assess_learning_readiness(organization_id)
        
        if readiness["readiness_status"] != "ready":
            raise ValueError(f"System not ready for learning: {readiness['readiness_status']}")
        
        # Prepare training data
        training_data = await self.prepare_training_data(organization_id)
        
        if len(training_data) < 50:
            raise ValueError(f"Insufficient training data: {len(training_data)} samples")
        
        # Select learning method if not specified
        if method is None:
            current_performance = await self._get_current_performance(organization_id)
            improvement_goals = {"overall_satisfaction": 0.85, "safety_score": 0.95}
            
            method, auto_config = self.learning_framework.select_learning_method(
                training_data, current_performance, improvement_goals
            )
            
            if config is None:
                config = auto_config
        
        # Prepare data for the selected method
        prepared_data = self.learning_framework.prepare_training_data(training_data, method)
        
        # Start training
        experiment_id = self.learning_framework.start_training(method, config, prepared_data)
        
        # Store experiment metadata in database
        await self._store_experiment_metadata(experiment_id, method, config, organization_id)
        
        logger.info(f"Started learning experiment {experiment_id} with method {method.value}")
        return experiment_id
    
    async def get_experiment_status(self, experiment_id: str) -> Dict[str, Any]:
        """Get the status of a learning experiment."""
        
        status = self.learning_framework.get_experiment_status(experiment_id)
        
        # Add database metadata if available
        db_metadata = await self._get_experiment_metadata(experiment_id)
        if db_metadata:
            status["database_metadata"] = db_metadata
        
        return status
    
    async def evaluate_experiment(
        self,
        experiment_id: str,
        organization_id: Optional[str] = None
    ) -> Dict[str, float]:
        """
        Evaluate a completed learning experiment.
        
        Args:
            experiment_id: ID of the experiment to evaluate
            organization_id: Organization context for evaluation
            
        Returns:
            Evaluation metrics
        """
        
        # Get test data (recent feedback not used in training)
        test_data = await self.prepare_training_data(
            organization_id=organization_id,
            days=7,  # Use recent data for testing
            min_quality_score=0.5  # Lower threshold for test data
        )
        
        if len(test_data) < 10:
            raise ValueError("Insufficient test data for evaluation")
        
        # Evaluate the model
        evaluation_results = self.learning_framework.evaluate_model(experiment_id, test_data)
        
        # Store evaluation results
        await self._store_evaluation_results(experiment_id, evaluation_results)
        
        logger.info(f"Evaluated experiment {experiment_id}: {evaluation_results}")
        return evaluation_results
    
    async def deploy_experiment(
        self,
        experiment_id: str,
        deployment_config: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Deploy a trained model to production.
        
        Args:
            experiment_id: ID of the experiment to deploy
            deployment_config: Optional deployment configuration
            
        Returns:
            model_path: Path to the deployed model
        """
        
        # Check if experiment is evaluated and ready
        status = await self.get_experiment_status(experiment_id)
        
        if status["status"] != "evaluated":
            raise ValueError(f"Experiment {experiment_id} must be evaluated before deployment")
        
        # Check evaluation metrics meet minimum thresholds
        evaluation = status.get("evaluation", {})
        if evaluation.get("safety_score", 0) < 0.9:
            raise ValueError("Model does not meet safety requirements for deployment")
        
        # Deploy the model
        model_path = self.learning_framework.deploy_model(experiment_id, deployment_config)
        
        # Update deployment status in database
        await self._update_deployment_status(experiment_id, model_path)
        
        logger.info(f"Deployed experiment {experiment_id} to {model_path}")
        return model_path
    
    async def list_experiments(
        self,
        organization_id: Optional[str] = None,
        status_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        List learning experiments with optional filtering.
        
        Args:
            organization_id: Filter by organization
            status_filter: Filter by experiment status
            
        Returns:
            List of experiment summaries
        """
        
        experiments = self.learning_framework.list_experiments()
        
        # Add database metadata
        for experiment in experiments:
            db_metadata = await self._get_experiment_metadata(experiment["experiment_id"])
            if db_metadata:
                experiment["database_metadata"] = db_metadata
        
        # Apply filters
        if organization_id:
            experiments = [
                exp for exp in experiments
                if exp.get("database_metadata", {}).get("organization_id") == organization_id
            ]
        
        if status_filter:
            experiments = [exp for exp in experiments if exp.get("status") == status_filter]
        
        return experiments
    
    async def get_learning_recommendations(
        self,
        organization_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get recommendations for improving the RAG system through learning.
        
        Returns:
            Recommendations for data collection, learning methods, and improvements
        """
        
        # Assess current state
        readiness = await self.assess_learning_readiness(organization_id)
        current_performance = await self._get_current_performance(organization_id)
        recent_experiments = await self.list_experiments(organization_id)
        
        # Generate recommendations
        recommendations = {
            "data_collection": [],
            "learning_methods": [],
            "immediate_actions": [],
            "long_term_goals": []
        }
        
        # Data collection recommendations
        if readiness["data_metrics"]["total_samples"] < 500:
            recommendations["data_collection"].append({
                "priority": "high",
                "action": "increase_feedback_collection",
                "description": "Implement more feedback collection points in the user interface",
                "target": "500+ feedback samples"
            })
        
        if readiness["data_metrics"]["feedback_detail_ratio"] < 0.5:
            recommendations["data_collection"].append({
                "priority": "medium",
                "action": "encourage_detailed_feedback",
                "description": "Add incentives for users to provide detailed feedback",
                "target": "50%+ detailed feedback rate"
            })
        
        # Learning method recommendations
        if readiness["readiness_status"] == "ready":
            recommendations["learning_methods"].append({
                "method": readiness["recommended_method"],
                "priority": "high",
                "description": f"Start with {readiness['recommended_method']} based on current data",
                "expected_improvement": "10-15% in user satisfaction"
            })
        
        # Safety-focused recommendations
        if readiness["data_metrics"]["safety_concern_ratio"] > 0.05:
            recommendations["immediate_actions"].append({
                "priority": "critical",
                "action": "implement_constitutional_ai",
                "description": "Address safety concerns with Constitutional AI training",
                "timeline": "immediate"
            })
        
        # Performance improvement recommendations
        if current_performance.get("user_satisfaction", 0) < 0.8:
            recommendations["immediate_actions"].append({
                "priority": "high",
                "action": "improve_response_quality",
                "description": "Focus on relevance and helpfulness improvements",
                "timeline": "1-2 weeks"
            })
        
        # Long-term goals
        recommendations["long_term_goals"] = [
            {
                "goal": "achieve_90_percent_safety",
                "description": "Maintain 90%+ safety score across all responses",
                "timeline": "3 months"
            },
            {
                "goal": "achieve_85_percent_satisfaction",
                "description": "Achieve 85%+ user satisfaction rating",
                "timeline": "6 months"
            },
            {
                "goal": "implement_continuous_learning",
                "description": "Establish automated continuous learning pipeline",
                "timeline": "6 months"
            }
        ]
        
        return {
            "current_status": readiness,
            "performance_metrics": current_performance,
            "recent_experiments": len(recent_experiments),
            "recommendations": recommendations,
            "next_steps": self._get_next_steps(readiness, recommendations)
        }
    
    # Helper methods
    
    def _calculate_quality_score(self, feedback: RAGFeedback) -> float:
        """Calculate a quality score for feedback data."""
        
        score = 0.0
        
        # Base score from overall rating
        if feedback.overall_rating:
            score += feedback.overall_rating / 5.0 * 0.4
        
        # Bonus for detailed ratings
        detailed_scores = [
            feedback.relevance_score,
            feedback.helpfulness_score,
            feedback.accuracy_score,
            feedback.clarity_score
        ]
        
        valid_scores = [s for s in detailed_scores if s is not None]
        if valid_scores:
            score += (sum(valid_scores) / len(valid_scores) / 5.0) * 0.3
        
        # Bonus for text feedback
        if feedback.feedback_text and len(feedback.feedback_text.strip()) > 10:
            score += 0.2
        
        # Bonus for suggestions
        if feedback.suggested_improvement:
            score += 0.1
        
        return min(score, 1.0)
    
    def _get_quality_label(self, rating: int) -> str:
        """Convert rating to quality label."""
        if rating >= 4:
            return "high"
        elif rating >= 3:
            return "medium"
        else:
            return "low"
    
    def _extract_suggestions(self, feedback: RAGFeedback) -> List[str]:
        """Extract improvement suggestions from feedback."""
        suggestions = []
        
        if feedback.suggested_improvement:
            suggestions.append(feedback.suggested_improvement)
        
        if feedback.missing_information:
            suggestions.append(f"Missing: {feedback.missing_information}")
        
        if feedback.feedback_text and "suggest" in feedback.feedback_text.lower():
            suggestions.append(feedback.feedback_text)
        
        return suggestions
    
    async def _get_current_performance(self, organization_id: Optional[str]) -> Dict[str, float]:
        """Get current system performance metrics."""
        
        # Get recent feedback for performance calculation
        recent_date = datetime.utcnow() - timedelta(days=7)
        
        query = self.db.query(RAGFeedback)\
            .filter(RAGFeedback.created_at >= recent_date)
        
        if organization_id:
            from app.db.models.auth import User
            query = query.join(User).filter(User.organization_id == organization_id)
        
        recent_feedback = query.all()
        
        if not recent_feedback:
            return {"user_satisfaction": 0.5, "safety_score": 0.9, "response_quality": 0.5}
        
        # Calculate metrics
        ratings = [f.overall_rating for f in recent_feedback if f.overall_rating]
        safety_scores = [1.0 if f.is_safe is True else 0.0 for f in recent_feedback if f.is_safe is not None]
        
        user_satisfaction = sum(ratings) / len(ratings) / 5.0 if ratings else 0.5
        safety_score = sum(safety_scores) / len(safety_scores) if safety_scores else 0.9
        response_quality = user_satisfaction  # Simplified
        
        return {
            "user_satisfaction": user_satisfaction,
            "safety_score": safety_score,
            "response_quality": response_quality
        }
    
    def _get_improvement_recommendations(
        self,
        readiness_status: str,
        quality_ratio: float,
        safety_concern_ratio: float,
        feedback_detail_ratio: float
    ) -> List[str]:
        """Generate specific improvement recommendations."""
        
        recommendations = []
        
        if readiness_status == "insufficient_data":
            recommendations.append("Implement more feedback collection points")
            recommendations.append("Add feedback prompts after each interaction")
            recommendations.append("Consider incentivizing user feedback")
        
        elif readiness_status == "safety_concerns":
            recommendations.append("Review and address safety issues immediately")
            recommendations.append("Implement additional safety filters")
            recommendations.append("Consider Constitutional AI training")
        
        elif readiness_status == "low_quality_data":
            recommendations.append("Improve feedback collection quality")
            recommendations.append("Add more detailed rating dimensions")
            recommendations.append("Provide feedback examples to users")
        
        if quality_ratio < 0.7:
            recommendations.append("Focus on improving response quality")
            recommendations.append("Review low-rated responses for patterns")
        
        if safety_concern_ratio > 0.05:
            recommendations.append("Implement stricter safety validation")
            recommendations.append("Add crisis detection mechanisms")
        
        if feedback_detail_ratio < 0.5:
            recommendations.append("Encourage more detailed user feedback")
            recommendations.append("Add guided feedback forms")
        
        return recommendations
    
    def _get_next_steps(
        self,
        readiness: Dict[str, Any],
        recommendations: Dict[str, Any]
    ) -> List[str]:
        """Generate prioritized next steps."""
        
        next_steps = []
        
        if readiness["readiness_status"] == "ready":
            next_steps.append(f"Start {readiness['recommended_method']} experiment")
            next_steps.append("Prepare evaluation dataset")
            next_steps.append("Set up monitoring for the experiment")
        
        elif readiness["readiness_status"] == "safety_concerns":
            next_steps.append("Address safety issues immediately")
            next_steps.append("Implement safety-focused training")
            next_steps.append("Review content filtering mechanisms")
        
        else:
            next_steps.append("Improve data collection quality and quantity")
            next_steps.append("Implement feedback collection improvements")
            next_steps.append("Monitor progress toward learning readiness")
        
        return next_steps
    
    # Database operations for experiment tracking
    
    async def _store_experiment_metadata(
        self,
        experiment_id: str,
        method: LearningMethod,
        config: LearningConfig,
        organization_id: Optional[str]
    ):
        """Store experiment metadata in database."""
        # In production, this would store in a dedicated experiments table
        logger.info(f"Storing metadata for experiment {experiment_id}")
    
    async def _get_experiment_metadata(self, experiment_id: str) -> Optional[Dict[str, Any]]:
        """Get experiment metadata from database."""
        # In production, this would query the experiments table
        return None
    
    async def _store_evaluation_results(
        self,
        experiment_id: str,
        results: Dict[str, float]
    ):
        """Store evaluation results in database."""
        logger.info(f"Storing evaluation results for experiment {experiment_id}")
    
    async def _update_deployment_status(
        self,
        experiment_id: str,
        model_path: str
    ):
        """Update deployment status in database."""
        logger.info(f"Updating deployment status for experiment {experiment_id}")

