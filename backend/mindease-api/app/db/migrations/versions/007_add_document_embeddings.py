"""
Add document embeddings and vector search support

Revision ID: 007
Revises: 006
Create Date: 2025-06-10
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from pgvector.sqlalchemy import Vector

# revision identifiers, used by Alembic
revision = '007_add_doc_embeddings'
down_revision = '006_add_conversation_tables'
branch_labels = None
depends_on = None


def upgrade():
    # Ensure pgvector extension is available
    op.execute('CREATE EXTENSION IF NOT EXISTS vector;')
    
    # Create documents table
    op.create_table(
        'documents',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('category', sa.String(length=100), nullable=True),
        sa.Column('source', sa.String(length=255), nullable=True),
        sa.Column('doc_metadata', sa.JSON(), nullable=True),
        sa.Column('organization_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_documents_category'), 'documents', ['category'], unique=False)
    op.create_index(op.f('ix_documents_organization_id'), 'documents', ['organization_id'], unique=False)
    op.create_index(op.f('ix_documents_title'), 'documents', ['title'], unique=False)

    # Create document_embeddings table with vector support
    op.create_table(
        'document_embeddings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('document_id', sa.Integer(), nullable=False),
        sa.Column('chunk_index', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('chunk_text', sa.Text(), nullable=False),
        sa.Column('embedding', postgresql.ARRAY(sa.Float()), nullable=False),
        sa.Column('embedding_model', sa.String(length=100), nullable=False, server_default='all-MiniLM-L6-v2'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['document_id'], ['documents.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_document_embeddings_document_id'), 'document_embeddings', ['document_id'], unique=False)
    op.create_index(op.f('ix_document_embeddings_chunk_index'), 'document_embeddings', ['chunk_index'], unique=False)
    
    # Create index for vector similarity search (using array for now, will convert to vector type later)
    # Note: This will be updated when pgvector is properly configured
    

def downgrade():
    # Drop tables in reverse order
    op.drop_index(op.f('ix_document_embeddings_chunk_index'), table_name='document_embeddings')
    op.drop_index(op.f('ix_document_embeddings_document_id'), table_name='document_embeddings')
    op.drop_table('document_embeddings')
    
    op.drop_index(op.f('ix_documents_title'), table_name='documents')
    op.drop_index(op.f('ix_documents_organization_id'), table_name='documents')
    op.drop_index(op.f('ix_documents_category'), table_name='documents')
    op.drop_table('documents')

