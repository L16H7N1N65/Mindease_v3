"""
Create missing conversation and chat analytics tables

Revision ID: 006
Revises: 005
Create Date: 2025-06-10
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic
revision = '006_add_conversation_tables'
down_revision = '005_add_organization_tables'
branch_labels = None
depends_on = None


def upgrade():
    # Create conversations table
    op.create_table(
        'conversations',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=True),
        sa.Column('language', sa.String(length=10), nullable=False, server_default='en'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_conversations_user_id'), 'conversations', ['user_id'], unique=False)

    # Create conversation_messages table
    op.create_table(
        'conversation_messages',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('conversation_id', sa.String(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('role', sa.String(length=20), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('sources', sa.JSON(), nullable=True),
        sa.Column('user_context', sa.JSON(), nullable=True),
        sa.Column('crisis_detected', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('language', sa.String(length=10), nullable=False, server_default='en'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['conversation_id'], ['conversations.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_conversation_messages_conversation_id'), 'conversation_messages', ['conversation_id'], unique=False)
    op.create_index(op.f('ix_conversation_messages_user_id'), 'conversation_messages', ['user_id'], unique=False)

    # Create chat_analytics table
    op.create_table(
        'chat_analytics',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('date', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('total_messages', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('total_conversations', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('crisis_events', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('avg_response_time', sa.Float(), nullable=True),
        sa.Column('most_used_categories', sa.JSON(), nullable=True),
        sa.Column('language_usage', sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_chat_analytics_user_id'), 'chat_analytics', ['user_id'], unique=False)
    op.create_index(op.f('ix_chat_analytics_date'), 'chat_analytics', ['date'], unique=False)

    # Create chat_feedback table
    op.create_table(
        'chat_feedback',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('message_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('rating', sa.Integer(), nullable=False),
        sa.Column('feedback_text', sa.Text(), nullable=True),
        sa.Column('helpful_sources', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['message_id'], ['conversation_messages.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_chat_feedback_message_id'), 'chat_feedback', ['message_id'], unique=False)
    op.create_index(op.f('ix_chat_feedback_user_id'), 'chat_feedback', ['user_id'], unique=False)

    # Create chat_settings table
    op.create_table(
        'chat_settings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('language', sa.String(length=10), nullable=False, server_default='en'),
        sa.Column('include_mood_context', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('include_therapy_context', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('crisis_alerts', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('conversation_memory', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('max_conversation_history', sa.Integer(), nullable=False, server_default='10'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id')
    )
    op.create_index(op.f('ix_chat_settings_user_id'), 'chat_settings', ['user_id'], unique=True)


def downgrade():
    # Drop tables in reverse order
    op.drop_index(op.f('ix_chat_settings_user_id'), table_name='chat_settings')
    op.drop_table('chat_settings')
    
    op.drop_index(op.f('ix_chat_feedback_user_id'), table_name='chat_feedback')
    op.drop_index(op.f('ix_chat_feedback_message_id'), table_name='chat_feedback')
    op.drop_table('chat_feedback')
    
    op.drop_index(op.f('ix_chat_analytics_date'), table_name='chat_analytics')
    op.drop_index(op.f('ix_chat_analytics_user_id'), table_name='chat_analytics')
    op.drop_table('chat_analytics')
    
    op.drop_index(op.f('ix_conversation_messages_user_id'), table_name='conversation_messages')
    op.drop_index(op.f('ix_conversation_messages_conversation_id'), table_name='conversation_messages')
    op.drop_table('conversation_messages')
    
    op.drop_index(op.f('ix_conversations_user_id'), table_name='conversations')
    op.drop_table('conversations')

