"""
Add therapy tables.

Revision ID: 003
Revises: 002
Create Date: 2025-04-28
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic
revision = '003_add_therapy_tables'
down_revision = '002_add_mood_tables'
branch_labels = None
depends_on = None


def upgrade():
    # Create therapy_exercises table
    op.create_table(
        'therapy_exercises',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('instructions', sa.Text(), nullable=True),
        sa.Column('duration', sa.Integer(), nullable=True),
        sa.Column('difficulty', sa.String(length=20), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create therapy_sessions table
    op.create_table(
        'therapy_sessions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('exercise_id', sa.Integer(), nullable=False),
        sa.Column('duration', sa.Integer(), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('completed', sa.Boolean(), nullable=False, default=False),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['exercise_id'], ['therapy_exercises.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create therapy_programs table
    op.create_table(
        'therapy_programs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create program_exercises table (many-to-many)
    op.create_table(
        'program_exercises',
        sa.Column('program_id', sa.Integer(), nullable=False),
        sa.Column('exercise_id', sa.Integer(), nullable=False),
        sa.Column('order', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['exercise_id'], ['therapy_exercises.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['program_id'], ['therapy_programs.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('program_id', 'exercise_id')
    )
    
    # Insert default exercises
    op.execute(
        """
        INSERT INTO therapy_exercises (name, description, instructions, duration, difficulty) VALUES
        ('Deep Breathing', 'Simple deep breathing exercise', 'Breathe in for 4 seconds, hold for 4 seconds, exhale for 4 seconds', 300, 'easy'),
        ('Progressive Muscle Relaxation', 'Tense and relax muscle groups', 'Tense each muscle group for 5 seconds, then relax for 10 seconds', 600, 'medium'),
        ('Mindfulness Meditation', 'Focus on the present moment', 'Sit comfortably, focus on your breath, and observe thoughts without judgment', 900, 'medium'),
        ('Body Scan', 'Scan your body for tension', 'Start at your toes and work up to your head, noticing sensations', 600, 'easy'),
        ('Visualization', 'Visualize a peaceful scene', 'Close your eyes and imagine a calm, peaceful place', 600, 'medium')
        """
    )


def downgrade():
    # Drop tables in reverse order
    op.drop_table('program_exercises')
    op.drop_table('therapy_programs')
    op.drop_table('therapy_sessions')
    op.drop_table('therapy_exercises')
