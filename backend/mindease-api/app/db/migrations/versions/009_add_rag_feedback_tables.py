"""
Add RAG feedback tables

Revision ID: 009_add_rag_feedback_tables
Revises: 008_add_admin_organization_support
Create Date: 2024-06-10 20:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = '009_add_rag_feedback_tables'
down_revision = '008_add_admin_org_support'
branch_labels = None
depends_on = None


def upgrade():
    """Add RAG feedback and learning tables."""
    
    # Create RAG feedback table
    op.create_table(
        'rag_feedback',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('conversation_id', sa.String(), nullable=False),
        sa.Column('message_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('organization_id', sa.Integer(), nullable=True),
        
        # User feedback ratings (1-5 scale)
        sa.Column('relevance_rating', sa.Integer(), nullable=True),
        sa.Column('helpfulness_rating', sa.Integer(), nullable=True),
        sa.Column('accuracy_rating', sa.Integer(), nullable=True),
        sa.Column('clarity_rating', sa.Integer(), nullable=True),
        sa.Column('safety_rating', sa.Integer(), nullable=True),
        
        # Overall feedback
        sa.Column('overall_rating', sa.Float(), nullable=True),
        sa.Column('feedback_text', sa.Text(), nullable=True),
        sa.Column('improvement_suggestions', sa.Text(), nullable=True),
        
        # Mental health context
        sa.Column('query_intent', sa.String(100), nullable=True),
        sa.Column('emotional_state', sa.String(50), nullable=True),
        sa.Column('crisis_level', sa.String(20), nullable=True),
        sa.Column('safety_concerns', sa.Boolean(), nullable=True, default=False),
        
        # System metadata
        sa.Column('response_time_ms', sa.Integer(), nullable=True),
        sa.Column('documents_retrieved', sa.Integer(), nullable=True),
        sa.Column('retrieval_method', sa.String(50), nullable=True),
        sa.Column('model_version', sa.String(50), nullable=True),
        
        # Timestamps
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        
        # sa.PrimaryKey('id'),
        sa.ForeignKeyConstraint(['conversation_id'], ['conversations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['message_id'], ['conversation_messages.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
    )
    
    # Create feedback analytics table
    op.create_table(
        'feedback_analytics',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('organization_id', sa.Integer(), nullable=True),
        sa.Column('date', sa.Date(), nullable=False),
        
        # Aggregated metrics
        sa.Column('total_feedback', sa.Integer(), nullable=False, default=0),
        sa.Column('average_rating', sa.Float(), nullable=True),
        sa.Column('safety_concern_count', sa.Integer(), nullable=False, default=0),
        sa.Column('improvement_suggestion_count', sa.Integer(), nullable=False, default=0),
        
        # Rating distributions
        sa.Column('rating_distribution', postgresql.JSONB(), nullable=True),
        sa.Column('intent_performance', postgresql.JSONB(), nullable=True),
        sa.Column('emotional_state_performance', postgresql.JSONB(), nullable=True),
        
        # Trends
        sa.Column('rating_trend', sa.Float(), nullable=True),
        sa.Column('safety_trend', sa.Float(), nullable=True),
        
        # Timestamps
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        
        # sa.PrimaryKey('id'),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('organization_id', 'date', name='uq_feedback_analytics_org_date'),
    )
    
    # Create feedback training data table
    op.create_table(
        'feedback_training_data',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('feedback_id', sa.String(), nullable=False),
        sa.Column('organization_id', sa.Integer(), nullable=True),
        
        # Training features
        sa.Column('query_text', sa.Text(), nullable=False),
        sa.Column('response_text', sa.Text(), nullable=False),
        sa.Column('retrieved_documents', postgresql.JSONB(), nullable=True),
        sa.Column('context_metadata', postgresql.JSONB(), nullable=True),
        
        # Labels for training
        sa.Column('feedback_score', sa.Float(), nullable=False),
        sa.Column('safety_score', sa.Float(), nullable=False),
        sa.Column('relevance_score', sa.Float(), nullable=False),
        sa.Column('improvement_suggestions', sa.Text(), nullable=True),
        
        # Data quality
        sa.Column('data_quality_score', sa.Float(), nullable=True),
        sa.Column('is_training_ready', sa.Boolean(), nullable=True, default=False),
        sa.Column('training_split', sa.String(20), nullable=True),  # train, validation, test
        
        # Timestamps
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        
        # sa.PrimaryKey('id'),
        sa.ForeignKeyConstraint(['feedback_id'], ['rag_feedback.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
    )
    
    # Create response improvement table
    op.create_table(
        'response_improvements',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('organization_id', sa.Integer(), nullable=True),
        sa.Column('created_by',    sa.Integer(), nullable=False),
        
        # Improvement details
        sa.Column('improvement_type', sa.String(50), nullable=False),  # document_update, model_retrain, prompt_engineering
        sa.Column('priority', sa.String(20), nullable=False),  # critical, high, medium, low
        sa.Column('status', sa.String(20), nullable=False, default='planned'),  # planned, in_progress, completed, cancelled
        
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('feedback_analysis', postgresql.JSONB(), nullable=True),
        
        # Implementation tracking
        sa.Column('implementation_plan', sa.Text(), nullable=True),
        sa.Column('implementation_notes', sa.Text(), nullable=True),
        sa.Column('completion_date', sa.DateTime(timezone=True), nullable=True),
        
        # Impact measurement
        sa.Column('before_metrics', postgresql.JSONB(), nullable=True),
        sa.Column('after_metrics', postgresql.JSONB(), nullable=True),
        sa.Column('impact_score', sa.Float(), nullable=True),
        
        # Timestamps
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        
        # sa.PrimaryKey('id'),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ondelete='CASCADE'),
    )
    
    # Create indexes for performance
    op.create_index('idx_rag_feedback_user_id', 'rag_feedback', ['user_id'])
    op.create_index('idx_rag_feedback_organization_id', 'rag_feedback', ['organization_id'])
    op.create_index('idx_rag_feedback_created_at', 'rag_feedback', ['created_at'])
    op.create_index('idx_rag_feedback_overall_rating', 'rag_feedback', ['overall_rating'])
    op.create_index('idx_rag_feedback_safety_concerns', 'rag_feedback', ['safety_concerns'])
    op.create_index('idx_rag_feedback_query_intent', 'rag_feedback', ['query_intent'])
    
    op.create_index('idx_feedback_analytics_organization_date', 'feedback_analytics', ['organization_id', 'date'])
    op.create_index('idx_feedback_analytics_date', 'feedback_analytics', ['date'])
    
    op.create_index('idx_feedback_training_data_organization', 'feedback_training_data', ['organization_id'])
    op.create_index('idx_feedback_training_data_training_ready', 'feedback_training_data', ['is_training_ready'])
    op.create_index('idx_feedback_training_data_split', 'feedback_training_data', ['training_split'])
    
    op.create_index('idx_response_improvements_organization', 'response_improvements', ['organization_id'])
    op.create_index('idx_response_improvements_status', 'response_improvements', ['status'])
    op.create_index('idx_response_improvements_priority', 'response_improvements', ['priority'])
    op.create_index('idx_response_improvements_type', 'response_improvements', ['improvement_type'])


def downgrade():
    """Remove RAG feedback and learning tables."""
    
    # Drop indexes
    op.drop_index('idx_response_improvements_type')
    op.drop_index('idx_response_improvements_priority')
    op.drop_index('idx_response_improvements_status')
    op.drop_index('idx_response_improvements_organization')
    
    op.drop_index('idx_feedback_training_data_split')
    op.drop_index('idx_feedback_training_data_training_ready')
    op.drop_index('idx_feedback_training_data_organization')
    
    op.drop_index('idx_feedback_analytics_date')
    op.drop_index('idx_feedback_analytics_organization_date')
    
    op.drop_index('idx_rag_feedback_query_intent')
    op.drop_index('idx_rag_feedback_safety_concerns')
    op.drop_index('idx_rag_feedback_overall_rating')
    op.drop_index('idx_rag_feedback_created_at')
    op.drop_index('idx_rag_feedback_organization_id')
    op.drop_index('idx_rag_feedback_user_id')
    
    # Drop tables
    op.drop_table('response_improvements')
    op.drop_table('feedback_training_data')
    op.drop_table('feedback_analytics')
    op.drop_table('rag_feedback')

