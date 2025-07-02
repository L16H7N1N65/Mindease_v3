"""
Initial database schema.

Revision ID: 001
Revises: 
Create Date: 2025-04-28
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic
revision = '001_initial_schema'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Create extension for vector operations
    op.execute('CREATE EXTENSION IF NOT EXISTS vector;')
    
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(length=50), nullable=False),
        sa.Column('email', sa.String(length=100), nullable=False),
        sa.Column('hashed_password', sa.String(length=100), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('terms_accepted', sa.Boolean(), nullable=False, default=False),
        sa.Column('terms_accepted_at', sa.DateTime(), nullable=True),
        sa.Column('email_confirmed', sa.Boolean(), nullable=False, default=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email'),
        sa.UniqueConstraint('username')
    )
    
    # Create roles table
    op.create_table(
        'roles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=50), nullable=False),
        sa.Column('description', sa.String(length=200), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    
    # Create permissions table
    op.create_table(
        'permissions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=50), nullable=False),
        sa.Column('description', sa.String(length=200), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    
    # Create user_roles table (many-to-many)
    op.create_table(
        'user_roles',
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('role_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['role_id'], ['roles.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('user_id', 'role_id')
    )
    
    # Create role_permissions table (many-to-many)
    op.create_table(
        'role_permissions',
        sa.Column('role_id', sa.Integer(), nullable=False),
        sa.Column('permission_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['permission_id'], ['permissions.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['role_id'], ['roles.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('role_id', 'permission_id')
    )
    
    # Create profiles table
    op.create_table(
        'profiles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('first_name', sa.String(length=50), nullable=True),
        sa.Column('last_name', sa.String(length=50), nullable=True),
        sa.Column('bio', sa.Text(), nullable=True),
        sa.Column('avatar_url', sa.String(length=200), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id')
    )
    
    # Create preferences table
    op.create_table(
        'preferences',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('theme', sa.String(length=20), nullable=True),
        sa.Column('language', sa.String(length=10), nullable=True),
        sa.Column('notifications_enabled', sa.Boolean(), nullable=False, default=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id')
    )
    
    # # Create documents table
    # op.create_table(
    #     'documents',
    #     sa.Column('id', sa.Integer(), nullable=False),
    #     sa.Column('content', sa.Text(), nullable=False),
    #     sa.Column('embedding', Vector(512), nullable=True),
    #     sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
    #     sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
    #     sa.PrimaryKeyConstraint('id')
    # )
    
    # # Create document_metadata table
    # op.create_table(
    #     'document_metadata',
    #     sa.Column('id', sa.Integer(), nullable=False),
    #     sa.Column('document_id', sa.Integer(), nullable=False),
    #     sa.Column('key', sa.String(length=50), nullable=False),
    #     sa.Column('value', sa.String(length=200), nullable=False),
    #     sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
    #     sa.ForeignKeyConstraint(['document_id'], ['documents.id'], ondelete='CASCADE'),
    #     sa.PrimaryKeyConstraint('id')
    # )
    
    # # Create index for vector search
    # op.create_index('idx_documents_embedding', 'documents', ['embedding'], postgresql_using='ivfflat')
    
    # Insert default roles
    op.execute(
        """
        INSERT INTO roles (name, description) VALUES
        ('admin', 'Administrator with full access'),
        ('user', 'Regular user with limited access')
        """
    )
    
    # Insert default permissions
    op.execute(
        """
        INSERT INTO permissions (name, description) VALUES
        ('user:read', 'Read user data'),
        ('user:write', 'Write user data'),
        ('user:delete', 'Delete user data'),
        ('document:read', 'Read documents'),
        ('document:write', 'Write documents'),
        ('document:delete', 'Delete documents'),
        ('admin:access', 'Access admin features')
        """
    )
    
    # Assign permissions to roles
    op.execute(
        """
        INSERT INTO role_permissions (role_id, permission_id)
        SELECT r.id, p.id
        FROM roles r, permissions p
        WHERE r.name = 'admin'
        """
    )
    
    op.execute(
        """
        INSERT INTO role_permissions (role_id, permission_id)
        SELECT r.id, p.id
        FROM roles r, permissions p
        WHERE r.name = 'user' AND p.name IN ('user:read', 'document:read')
        """
    )


def downgrade():
    # Drop tables in reverse order
    # op.drop_index('idx_documents_embedding', table_name='documents')
    # op.drop_table('document_metadata')
    # op.drop_table('documents')
    op.drop_table('preferences')
    op.drop_table('profiles')
    op.drop_table('role_permissions')
    op.drop_table('user_roles')
    op.drop_table('permissions')
    op.drop_table('roles')
    op.drop_table('users')
    
    # Drop extension
    op.execute('DROP EXTENSION IF EXISTS vector;')
