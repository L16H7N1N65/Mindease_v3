"""
Sync document_embeddings to match new ORM
( content, model_name, vector(384) )

Revision ID: 011_sync_document_embeddings
Revises: 010_add_user_org_to_documents
Create Date: 2025-06-20
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from pgvector.sqlalchemy import Vector

# ── identifiers ────────────────────────────────────────────────────────────
revision = "011_sync_document_embeddings"
down_revision = "010_add_user_org_to_documents"
branch_labels = None
depends_on = None


# ── helpers ────────────────────────────────────────────────────────────────
def _col_exists(table, column):
    bind = op.get_bind()
    return column in {c["name"] for c in sa.inspect(bind).get_columns(table)}


# ── upgrade ────────────────────────────────────────────────────────────────
def upgrade() -> None:
    # pgvector extension (safe if it already exists)
    op.execute("CREATE EXTENSION IF NOT EXISTS vector;")

    # rename chunk_text → content
    if _col_exists("document_embeddings", "chunk_text") and not _col_exists(
        "document_embeddings", "content"
    ):
        op.alter_column(
            "document_embeddings",
            "chunk_text",
            new_column_name="content",
            existing_type=sa.Text(),
        )

    # rename embedding_model → model_name
    if _col_exists("document_embeddings", "embedding_model") and not _col_exists(
        "document_embeddings", "model_name"
    ):
        op.alter_column(
            "document_embeddings",
            "embedding_model",
            new_column_name="model_name",
            existing_type=sa.String(length=100),
        )

    # drop chunk_index (and its index) if you no longer use it
    if _col_exists("document_embeddings", "chunk_index"):
        op.drop_index(
            "ix_document_embeddings_chunk_index", table_name="document_embeddings"
        )
        op.drop_column("document_embeddings", "chunk_index")

    # convert embedding from FLOAT[] → vector(384)
    if _col_exists("document_embeddings", "embedding"):
        op.alter_column(
            "document_embeddings",
            "embedding",
            existing_type=postgresql.ARRAY(sa.Float()),
            type_=Vector(384),
            postgresql_using="embedding::vector",
            nullable=False,
        )

    # create ivfflat index for fast similarity (skip if already present)
    op.execute(
        """
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM pg_indexes
                 WHERE tablename = 'document_embeddings'
                   AND indexname = 'ix_document_embeddings_embedding_l2'
            ) THEN
                CREATE INDEX ix_document_embeddings_embedding_l2
                  ON document_embeddings
                  USING ivfflat (embedding vector_l2_ops);
            END IF;
        END$$;
        """
    )


# ── downgrade (optional) ───────────────────────────────────────────────────
def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_document_embeddings_embedding_l2;")
    op.alter_column(
        "document_embeddings",
        "embedding",
        existing_type=Vector(384),
        type_=postgresql.ARRAY(sa.Float()),
        postgresql_using="embedding",
    )
    op.add_column(
        "document_embeddings",
        sa.Column("chunk_index", sa.Integer(), server_default="0", nullable=False),
    )
    op.create_index(
        "ix_document_embeddings_chunk_index",
        "document_embeddings",
        ["chunk_index"],
    )
    if _col_exists("document_embeddings", "model_name"):
        op.alter_column(
            "document_embeddings",
            "model_name",
            new_column_name="embedding_model",
            existing_type=sa.String(length=100),
        )
    if _col_exists("document_embeddings", "content"):
        op.alter_column(
            "document_embeddings",
            "content",
            new_column_name="chunk_text",
            existing_type=sa.Text(),
        )