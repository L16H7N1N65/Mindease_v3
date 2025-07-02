"""
Add social interaction tables.

Revision ID: 004
Revises: 003
Create Date: 2025-04-28
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic
revision = '004_add_social_tables'
down_revision = '003_add_therapy_tables'
branch_labels = None
depends_on = None


def upgrade():
    # Create social_posts table
    op.create_table(
        'social_posts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create comments table
    op.create_table(
        'comments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('post_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['post_id'], ['social_posts.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create likes table
    op.create_table(
        'likes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('post_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['post_id'], ['social_posts.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('post_id', 'user_id', name='uq_likes_post_user')
    )
    
    # Create tags table
    op.create_table(
        'tags',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('post_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['post_id'], ['social_posts.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes
    op.create_index('idx_social_posts_user_id', 'social_posts', ['user_id'])
    op.create_index('idx_social_posts_created_at', 'social_posts', ['created_at'])
    op.create_index('idx_comments_post_id', 'comments', ['post_id'])
    op.create_index('idx_comments_user_id', 'comments', ['user_id'])
    op.create_index('idx_likes_post_id', 'likes', ['post_id'])
    op.create_index('idx_likes_user_id', 'likes', ['user_id'])
    op.create_index('idx_tags_name', 'tags', ['name'])
    op.create_index('idx_tags_post_id', 'tags', ['post_id'])


def downgrade():
    # Drop tables in reverse order
    op.drop_index('idx_tags_post_id', table_name='tags')
    op.drop_index('idx_tags_name', table_name='tags')
    op.drop_index('idx_likes_user_id', table_name='likes')
    op.drop_index('idx_likes_post_id', table_name='likes')
    op.drop_index('idx_comments_user_id', table_name='comments')
    op.drop_index('idx_comments_post_id', table_name='comments')
    op.drop_index('idx_social_posts_created_at', table_name='social_posts')
    op.drop_index('idx_social_posts_user_id', table_name='social_posts')
    op.drop_table('tags')
    op.drop_table('likes')
    op.drop_table('comments')
    op.drop_table('social_posts')
