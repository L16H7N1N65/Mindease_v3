"""
RAG Learning Schemas

Pydantic schemas for RAG learning and continuous improvement API.
"""
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum


class LearningMethodEnum(str, Enum):
    """Available learning methods."""
    SUPERVISED_FINE_TUNING = "supervised_fine_tuning"
    PARAMETER_EFFICIENT_FINE_TUNING = "parameter_efficient_fine_tuning"
    REINFORCEMENT_LEARNING = "reinforcement_learning"
    RETRIEVAL_AUGMENTED_FINE_TUNING = "retrieval_augmented_fine_tuning"
    DIRECT_PREFERENCE_OPTIMIZATION = "direct_preference_optimization"
    CONSTITUTIONAL_AI = "constitutional_ai"


class ModelTypeEnum(str, Enum):
    """Types of models that can be fine-tuned."""
    EMBEDDING_MODEL = "embedding_model"
    LANGUAGE_MODEL = "language_model"
    RETRIEVAL_MODEL = "retrieval_model"
    RANKING_MODEL = "ranking_model"


class ExperimentStatusEnum(str, Enum):
    """Experiment status values."""
    CONFIGURED = "configured"
    TRAINING = "training"
    COMPLETED = "completed"
    EVALUATED = "evaluated"
    DEPLOYED = "deployed"
    FAILED = "failed"
    NOT_FOUND = "not_found"


class ReadinessStatusEnum(str, Enum):
    """Learning readiness status values."""
    READY = "ready"
    INSUFFICIENT_DATA = "insufficient_data"
    SAFETY_CONCERNS = "safety_concerns"
    LOW_QUALITY_DATA = "low_quality_data"


# Request Schemas

class LearningConfigRequest(BaseModel):
    """Configuration for learning experiments."""
    learning_rate: Optional[float] = Field(None, description="Learning rate for training")
    batch_size: Optional[int] = Field(None, description="Batch size for training")
    num_epochs: Optional[int] = Field(None, description="Number of training epochs")
    validation_split: Optional[float] = Field(0.2, description="Validation data split ratio")
    early_stopping_patience: Optional[int] = Field(3, description="Early stopping patience")
    use_lora: Optional[bool] = Field(True, description="Use LoRA for parameter efficient training")
    lora_rank: Optional[int] = Field(16, description="LoRA rank parameter")
    lora_alpha: Optional[int] = Field(32, description="LoRA alpha parameter")
    target_modules: Optional[List[str]] = Field(None, description="Target modules for LoRA")


class ExperimentCreateRequest(BaseModel):
    """Request to create a new learning experiment."""
    organization_id: Optional[str] = Field(None, description="Organization ID (uses current user's if not provided)")
    method: Optional[LearningMethodEnum] = Field(None, description="Learning method (auto-selected if not provided)")
    config: Optional[LearningConfigRequest] = Field(None, description="Custom learning configuration")
    description: Optional[str] = Field(None, description="Description of the experiment")
    tags: Optional[List[str]] = Field(None, description="Tags for organizing experiments")


# Response Schemas

class DataMetrics(BaseModel):
    """Metrics about available training data."""
    total_samples: int = Field(description="Total number of feedback samples")
    quality_samples: int = Field(description="Number of high-quality samples")
    safety_issues: int = Field(description="Number of samples with safety concerns")
    detailed_feedback: int = Field(description="Number of samples with detailed feedback")
    data_sufficiency: float = Field(description="Data sufficiency ratio (0-1)")
    quality_ratio: float = Field(description="Quality samples ratio (0-1)")
    safety_concern_ratio: float = Field(description="Safety concern ratio (0-1)")
    feedback_detail_ratio: float = Field(description="Detailed feedback ratio (0-1)")


class LearningReadinessResponse(BaseModel):
    """Response for learning readiness assessment."""
    readiness_status: ReadinessStatusEnum = Field(description="Overall readiness status")
    recommended_action: str = Field(description="Recommended next action")
    recommended_method: Optional[LearningMethodEnum] = Field(None, description="Recommended learning method")
    data_metrics: DataMetrics = Field(description="Detailed data metrics")
    recommendations: List[str] = Field(description="Specific improvement recommendations")


class ExperimentConfig(BaseModel):
    """Experiment configuration details."""
    experiment_id: str = Field(description="Unique experiment identifier")
    method: LearningMethodEnum = Field(description="Learning method used")
    config: Dict[str, Any] = Field(description="Training configuration")
    data_stats: Dict[str, Any] = Field(description="Training data statistics")
    start_time: str = Field(description="Experiment start time")


class ExperimentResults(BaseModel):
    """Experiment training results."""
    method: str = Field(description="Learning method used")
    model_path: str = Field(description="Path to trained model")
    training_loss: Optional[float] = Field(None, description="Final training loss")
    validation_loss: Optional[float] = Field(None, description="Final validation loss")
    epochs_completed: Optional[int] = Field(None, description="Number of epochs completed")
    training_time_minutes: Optional[float] = Field(None, description="Training time in minutes")
    additional_metrics: Optional[Dict[str, Any]] = Field(None, description="Additional method-specific metrics")


class ExperimentEvaluation(BaseModel):
    """Experiment evaluation results."""
    accuracy: Optional[float] = Field(None, description="Overall accuracy score")
    relevance_score: Optional[float] = Field(None, description="Response relevance score")
    safety_score: Optional[float] = Field(None, description="Safety score")
    user_satisfaction: Optional[float] = Field(None, description="User satisfaction score")
    additional_metrics: Optional[Dict[str, Any]] = Field(None, description="Additional evaluation metrics")


class ExperimentDeployment(BaseModel):
    """Experiment deployment information."""
    model_path: str = Field(description="Deployed model path")
    deployment_status: str = Field(description="Deployment status")
    deployment_time: Optional[str] = Field(None, description="Deployment timestamp")
    additional_info: Optional[Dict[str, Any]] = Field(None, description="Additional deployment info")


class ExperimentResponse(BaseModel):
    """Response for experiment operations."""
    experiment_id: str = Field(description="Unique experiment identifier")
    status: ExperimentStatusEnum = Field(description="Current experiment status")
    config: Optional[ExperimentConfig] = Field(None, description="Experiment configuration")
    results: Optional[ExperimentResults] = Field(None, description="Training results")
    evaluation: Optional[ExperimentEvaluation] = Field(None, description="Evaluation results")
    deployment: Optional[ExperimentDeployment] = Field(None, description="Deployment information")
    error: Optional[Dict[str, Any]] = Field(None, description="Error information if failed")
    database_metadata: Optional[Dict[str, Any]] = Field(None, description="Additional database metadata")
    message: Optional[str] = Field(None, description="Status message")


class ExperimentSummary(BaseModel):
    """Summary of an experiment for listing."""
    experiment_id: str = Field(description="Unique experiment identifier")
    status: ExperimentStatusEnum = Field(description="Current experiment status")
    method: Optional[str] = Field(None, description="Learning method used")
    start_time: Optional[str] = Field(None, description="Experiment start time")
    organization_id: Optional[str] = Field(None, description="Organization ID")
    description: Optional[str] = Field(None, description="Experiment description")
    tags: Optional[List[str]] = Field(None, description="Experiment tags")
    performance_summary: Optional[Dict[str, float]] = Field(None, description="Key performance metrics")


class ExperimentListResponse(BaseModel):
    """Response for listing experiments."""
    experiments: List[ExperimentSummary] = Field(description="List of experiments")
    total: int = Field(description="Total number of experiments")
    organization_id: Optional[str] = Field(None, description="Organization filter applied")
    status_filter: Optional[str] = Field(None, description="Status filter applied")


class RecommendationItem(BaseModel):
    """Individual recommendation item."""
    priority: str = Field(description="Priority level (critical, high, medium, low)")
    action: str = Field(description="Recommended action")
    description: str = Field(description="Detailed description")
    target: Optional[str] = Field(None, description="Target metric or goal")
    timeline: Optional[str] = Field(None, description="Recommended timeline")
    expected_improvement: Optional[str] = Field(None, description="Expected improvement")


class LearningRecommendations(BaseModel):
    """Learning improvement recommendations."""
    data_collection: List[RecommendationItem] = Field(description="Data collection recommendations")
    learning_methods: List[RecommendationItem] = Field(description="Learning method recommendations")
    immediate_actions: List[RecommendationItem] = Field(description="Immediate action items")
    long_term_goals: List[RecommendationItem] = Field(description="Long-term improvement goals")


class LearningRecommendationsResponse(BaseModel):
    """Response for learning recommendations."""
    current_status: LearningReadinessResponse = Field(description="Current system status")
    performance_metrics: Dict[str, float] = Field(description="Current performance metrics")
    recent_experiments: int = Field(description="Number of recent experiments")
    recommendations: LearningRecommendations = Field(description="Detailed recommendations")
    next_steps: List[str] = Field(description="Prioritized next steps")


# Training Data Schemas

class TrainingDataStats(BaseModel):
    """Statistics about training data."""
    total_samples: int = Field(description="Total number of samples")
    quality_distribution: Dict[str, int] = Field(description="Distribution by quality level")
    safety_issues: int = Field(description="Number of samples with safety issues")
    with_suggestions: int = Field(description="Number of samples with improvement suggestions")
    intent_distribution: Dict[str, int] = Field(description="Distribution by query intent")
    data_period_days: int = Field(description="Data collection period in days")
    organization_id: Optional[str] = Field(None, description="Organization ID")
    readiness_assessment: Dict[str, Union[bool, float]] = Field(description="Readiness assessment")


# Learning Method Information

class LearningMethodInfo(BaseModel):
    """Information about a learning method."""
    name: str = Field(description="Human-readable method name")
    description: str = Field(description="Method description")
    best_for: str = Field(description="Best use cases")
    data_requirements: str = Field(description="Data requirements")
    training_time: str = Field(description="Expected training time")
    resource_requirements: str = Field(description="Resource requirements")


class LearningMethodsResponse(BaseModel):
    """Response for listing learning methods."""
    methods: Dict[str, LearningMethodInfo] = Field(description="Available learning methods")
    selection_guidance: Dict[str, str] = Field(description="Method selection guidance")


# Error Schemas

class LearningError(BaseModel):
    """Error response for learning operations."""
    error_type: str = Field(description="Type of error")
    message: str = Field(description="Error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")
    suggestions: Optional[List[str]] = Field(None, description="Suggestions for resolution")


# Utility Schemas

class LearningProgress(BaseModel):
    """Progress information for ongoing learning."""
    experiment_id: str = Field(description="Experiment identifier")
    current_epoch: Optional[int] = Field(None, description="Current training epoch")
    total_epochs: Optional[int] = Field(None, description="Total planned epochs")
    current_loss: Optional[float] = Field(None, description="Current training loss")
    estimated_completion: Optional[str] = Field(None, description="Estimated completion time")
    progress_percentage: Optional[float] = Field(None, description="Progress percentage (0-100)")


class ModelPerformanceComparison(BaseModel):
    """Comparison between baseline and improved model."""
    baseline_metrics: Dict[str, float] = Field(description="Baseline model performance")
    improved_metrics: Dict[str, float] = Field(description="Improved model performance")
    improvement_deltas: Dict[str, float] = Field(description="Improvement deltas")
    statistical_significance: Optional[Dict[str, bool]] = Field(None, description="Statistical significance tests")


class DeploymentRequest(BaseModel):
    """Request for model deployment."""
    experiment_id: str = Field(description="Experiment to deploy")
    deployment_environment: Optional[str] = Field("production", description="Deployment environment")
    rollback_strategy: Optional[str] = Field("immediate", description="Rollback strategy")
    monitoring_config: Optional[Dict[str, Any]] = Field(None, description="Monitoring configuration")
    approval_required: Optional[bool] = Field(True, description="Whether approval is required")


class DeploymentResponse(BaseModel):
    """Response for model deployment."""
    experiment_id: str = Field(description="Deployed experiment ID")
    deployment_id: str = Field(description="Unique deployment ID")
    status: str = Field(description="Deployment status")
    model_path: str = Field(description="Deployed model path")
    deployment_time: str = Field(description="Deployment timestamp")
    rollback_info: Optional[Dict[str, Any]] = Field(None, description="Rollback information")
    monitoring_endpoints: Optional[List[str]] = Field(None, description="Monitoring endpoints")
    message: str = Field(description="Deployment message")

