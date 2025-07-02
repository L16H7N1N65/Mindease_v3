"""
Admin Schemas

Pydantic schemas for admin API endpoints.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class DatasetInfo(BaseModel):
    """Information about a dataset."""
    name: str
    category: Optional[str] = None
    document_count: int
    first_uploaded: datetime
    last_uploaded: datetime
    uploaded_by: Optional[str] = None
    organization_id: Optional[int] = None


class DatasetListResponse(BaseModel):
    """Response for dataset listing."""
    datasets: List[DatasetInfo]
    total_count: int
    limit: int
    offset: int


class ValidationResult(BaseModel):
    """Validation result for a single check."""
    category: str
    level: str
    message: str
    field: Optional[str] = None
    value: Optional[str] = None
    suggestion: Optional[str] = None


class ValidationReport(BaseModel):
    """Complete validation report."""
    total_items: int
    valid_items: int
    invalid_items: int
    warnings: int
    errors: int
    critical_issues: int
    success_rate: float
    is_valid: bool
    processing_time: float
    results: List[ValidationResult]


class LoadResults(BaseModel):
    """Results from data loading operation."""
    total_processed: int
    successful: int
    failed: int
    success_rate: float
    failed_documents: List[Dict[str, Any]] = []


class DatasetUploadResponse(BaseModel):
    """Response for dataset upload operation."""
    status: str
    message: str
    file_path: str
    dataset_name: Optional[str] = None
    processing_time: Optional[float] = None
    extracted_items: Optional[int] = None
    transformed_items: Optional[int] = None
    load_results: Optional[LoadResults] = None
    validation_report: Optional[ValidationReport] = None


class DatabaseStats(BaseModel):
    """Database statistics."""
    total_documents: int
    total_embeddings: int
    total_users: int
    total_conversations: int
    database_size: str
    documents_last_24h: int
    conversations_last_24h: int


class ResourceUsage(BaseModel):
    """System resource usage."""
    cpu_percent: float
    memory: Dict[str, Any]
    disk: Dict[str, Any]
    load_average: Optional[List[float]] = None


class StorageInfo(BaseModel):
    """Storage information."""
    upload_directory: Dict[str, Any]


class ServiceStatus(BaseModel):
    """Status of a service."""
    status: str
    response_time: Optional[str] = None
    error: Optional[str] = None


class SystemHealthResponse(BaseModel):
    """System health response."""
    timestamp: str
    status: str
    services: Dict[str, ServiceStatus]
    resources: ResourceUsage
    database: DatabaseStats
    storage: StorageInfo


class DailyCount(BaseModel):
    """Daily count data."""
    date: str
    count: int
    category: Optional[str] = None


class ConversationDailyCount(BaseModel):
    """Daily conversation count."""
    date: str
    count: int


class UserActivityCount(BaseModel):
    """Daily active user count."""
    date: str
    active_users: int


class DocumentAnalytics(BaseModel):
    """Document analytics."""
    daily_counts: List[DailyCount]
    total_period: int


class ConversationAnalytics(BaseModel):
    """Conversation analytics."""
    daily_counts: List[ConversationDailyCount]
    total_period: int


class UserAnalytics(BaseModel):
    """User activity analytics."""
    daily_active: List[UserActivityCount]
    total_active_period: int


class AnalyticsPeriod(BaseModel):
    """Analytics period information."""
    start_date: str
    end_date: str
    days: int


class AnalyticsResponse(BaseModel):
    """Analytics response."""
    period: AnalyticsPeriod
    documents: DocumentAnalytics
    conversations: ConversationAnalytics
    users: UserAnalytics
    embeddings: Dict[str, Any] = {}


class ResourceCleanupResponse(BaseModel):
    """Resource cleanup response."""
    status: str
    deleted_files: Optional[int] = None
    deleted_size: Optional[int] = None
    errors: List[str] = []
    cutoff_date: Optional[str] = None
    message: Optional[str] = None


class DatabaseOptimizationResponse(BaseModel):
    """Database optimization response."""
    status: str
    message: str
    timestamp: Optional[str] = None


class UserInfo(BaseModel):
    """User information for admin."""
    id: int
    email: str
    username: Optional[str] = None
    full_name: Optional[str] = None
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime] = None
    organization_id: Optional[int] = None
    document_count: int = 0
    conversation_count: int = 0


class UserListResponse(BaseModel):
    """Response for user listing."""
    users: List[UserInfo]
    total_count: int
    limit: int
    offset: int


class OrganizationInfo(BaseModel):
    """Organization information for admin."""
    id: int
    name: str
    description: Optional[str] = None
    is_active: bool
    created_at: datetime
    user_count: int = 0
    document_count: int = 0


class OrganizationListResponse(BaseModel):
    """Response for organization listing."""
    organizations: List[OrganizationInfo]
    total_count: int
    limit: int
    offset: int


class LogEntry(BaseModel):
    """System log entry."""
    timestamp: str
    level: str
    message: str
    module: str


class LogsResponse(BaseModel):
    """System logs response."""
    logs: List[LogEntry]
    total_count: int
    level_filter: str
    limit: int


class ETLTestRequest(BaseModel):
    """Request for ETL pipeline testing."""
    title: str = Field(..., description="Document title")
    content: str = Field(..., description="Document content")
    category: Optional[str] = Field(None, description="Document category")
    source: Optional[str] = Field(None, description="Document source")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class ETLTestResponse(BaseModel):
    """Response for ETL pipeline testing."""
    status: str
    validation_report: ValidationReport
    transformed_data: List[Dict[str, Any]]
    message: str


class DashboardData(BaseModel):
    """Admin dashboard data."""
    timestamp: str
    system_health: SystemHealthResponse
    analytics: AnalyticsResponse
    datasets: DatasetListResponse
    resources: ResourceUsage
    error: Optional[str] = None


# Configuration schemas

class AdminConfig(BaseModel):
    """Admin configuration."""
    max_upload_size: int = Field(default=100 * 1024 * 1024, description="Maximum upload size in bytes")
    allowed_file_types: List[str] = Field(default=["csv", "json", "txt", "zip"], description="Allowed file types")
    cleanup_days: int = Field(default=30, description="Days after which to clean up old files")
    batch_size: int = Field(default=100, description="Default batch size for processing")
    max_concurrent_uploads: int = Field(default=5, description="Maximum concurrent uploads")


class SystemConfig(BaseModel):
    """System configuration."""
    maintenance_mode: bool = Field(default=False, description="Whether system is in maintenance mode")
    max_documents_per_user: int = Field(default=10000, description="Maximum documents per user")
    max_conversations_per_user: int = Field(default=1000, description="Maximum conversations per user")
    embedding_model: str = Field(default="sentence-transformers/all-MiniLM-L6-v2", description="Embedding model name")
    auto_cleanup_enabled: bool = Field(default=True, description="Whether auto cleanup is enabled")


# Error schemas

class AdminError(BaseModel):
    """Admin error response."""
    error: str
    detail: str
    timestamp: str
    request_id: Optional[str] = None


class ValidationError(BaseModel):
    """Validation error response."""
    error: str
    validation_errors: List[ValidationResult]
    timestamp: str


# Utility schemas

class BulkOperationRequest(BaseModel):
    """Request for bulk operations."""
    operation: str = Field(..., description="Operation to perform")
    target_ids: List[int] = Field(..., description="Target IDs for the operation")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Operation parameters")


class BulkOperationResponse(BaseModel):
    """Response for bulk operations."""
    operation: str
    total_requested: int
    successful: int
    failed: int
    errors: List[str] = []
    results: List[Dict[str, Any]] = []


class MaintenanceRequest(BaseModel):
    """Request for maintenance operations."""
    operation: str = Field(..., description="Maintenance operation to perform")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Operation parameters")
    force: bool = Field(default=False, description="Whether to force the operation")


class MaintenanceResponse(BaseModel):
    """Response for maintenance operations."""
    operation: str
    status: str
    message: str
    started_at: str
    completed_at: Optional[str] = None
    duration: Optional[float] = None
    results: Dict[str, Any] = {}


# Export all schemas
__all__ = [
    "DatasetInfo",
    "DatasetListResponse", 
    "ValidationResult",
    "ValidationReport",
    "LoadResults",
    "DatasetUploadResponse",
    "DatabaseStats",
    "ResourceUsage",
    "StorageInfo",
    "ServiceStatus",
    "SystemHealthResponse",
    "DailyCount",
    "ConversationDailyCount",
    "UserActivityCount",
    "DocumentAnalytics",
    "ConversationAnalytics",
    "UserAnalytics",
    "AnalyticsPeriod",
    "AnalyticsResponse",
    "ResourceCleanupResponse",
    "DatabaseOptimizationResponse",
    "UserInfo",
    "UserListResponse",
    "OrganizationInfo",
    "OrganizationListResponse",
    "LogEntry",
    "LogsResponse",
    "ETLTestRequest",
    "ETLTestResponse",
    "DashboardData",
    "AdminConfig",
    "SystemConfig",
    "AdminError",
    "ValidationError",
    "BulkOperationRequest",
    "BulkOperationResponse",
    "MaintenanceRequest",
    "MaintenanceResponse"
]

