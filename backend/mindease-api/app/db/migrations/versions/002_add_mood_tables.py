"""
Add mood tracking tables.

Revision ID: 002
Revises: 001
Create Date: 2025-04-28
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic
revision = '002_add_mood_tables'
down_revision = '001_initial_schema'
branch_labels = None
depends_on = None


def upgrade():
    # Create mood_entries table
    op.create_table(
        'mood_entries',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('value', sa.Integer(), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.CheckConstraint('value >= 1 AND value <= 10', name='check_mood_value_range')
    )
    
    # Create mood_factors table
    op.create_table(
        'mood_factors',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('entry_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=50), nullable=False),
        sa.Column('impact', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['entry_id'], ['mood_entries.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.CheckConstraint('impact >= -5 AND impact <= 5', name='check_impact_range')
    )
    
    # Create indexes
    op.create_index('idx_mood_entries_user_id', 'mood_entries', ['user_id'])
    op.create_index('idx_mood_entries_created_at', 'mood_entries', ['created_at'])
    op.create_index('idx_mood_factors_entry_id', 'mood_factors', ['entry_id'])
    op.create_index('idx_mood_factors_name', 'mood_factors', ['name'])


def downgrade():
    # Drop tables in reverse order
    op.drop_index('idx_mood_factors_name', table_name='mood_factors')
    op.drop_index('idx_mood_factors_entry_id', table_name='mood_factors')
    op.drop_index('idx_mood_entries_created_at', table_name='mood_entries')
    op.drop_index('idx_mood_entries_user_id', table_name='mood_entries')
    op.drop_table('mood_factors')
    op.drop_table('mood_entries')
