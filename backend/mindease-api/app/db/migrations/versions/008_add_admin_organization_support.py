"""
Add admin and organization support to users table

Revision ID: 008
Revises: 007
Create Date: 2025-06-10
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic
revision = '008_add_admin_org_support'
down_revision = '007_add_doc_embeddings'
branch_labels = None
depends_on = None


def upgrade():
    # Add admin flag and organization relationship to users table
    op.add_column('users', sa.Column('is_admin', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('users', sa.Column('organization_id', sa.Integer(), nullable=True))
    
    # Create foreign key constraint for organization
    op.create_foreign_key(
        'fk_users_organization_id', 
        'users', 
        'organizations', 
        ['organization_id'], 
        ['id']
    )
    
    # Create index for organization_id
    op.create_index(op.f('ix_users_organization_id'), 'users', ['organization_id'], unique=False)


def downgrade():
    # Drop index and foreign key constraint
    op.drop_index(op.f('ix_users_organization_id'), table_name='users')
    op.drop_constraint('fk_users_organization_id', 'users', type_='foreignkey')
    
    # Drop columns
    op.drop_column('users', 'organization_id')
    op.drop_column('users', 'is_admin')

