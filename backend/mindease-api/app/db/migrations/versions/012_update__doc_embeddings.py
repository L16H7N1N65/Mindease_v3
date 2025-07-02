"""add updated_at to document_embeddings

Revision ID: 012_update__doc_embeddings
Revises: 011_sync_document_embeddings
Create Date: 2025-06-19
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from pgvector.sqlalchemy import Vector
# ---------------------------------------------------------------------------
revision      = "012_update__doc_embeddings"
down_revision = "011_sync_document_embeddings"
branch_labels = None
depends_on    = None
# ---------------------------------------------------------------------------


def _column_exists(table: str, col: str) -> bool:
    bind = op.get_bind()
    insp = sa.inspect(bind)
    return col in [c["name"] for c in insp.get_columns(table)]


# ────────────────────────── upgrade ────────────────────────────────────────
def upgrade():
    if not _column_exists("document_embeddings", "updated_at"):
        op.add_column(
            "document_embeddings",
            sa.Column(
                "updated_at",
                sa.DateTime(timezone=True),
                nullable=False,
                server_default=sa.func.now(),
            ),
        )

    # make sure created_at is there as well (older DBs sometimes miss it)
    if not _column_exists("document_embeddings", "created_at"):
        op.add_column(
            "document_embeddings",
            sa.Column(
                "created_at",
                sa.DateTime(timezone=True),
                nullable=False,
                server_default=sa.func.now(),
            ),
        )


# ───────────────────────── downgrade ───────────────────────────────────────
def downgrade():
    if _column_exists("document_embeddings", "updated_at"):
        op.drop_column("document_embeddings", "updated_at")
    if _column_exists("document_embeddings", "created_at"):
        # only drop if it was added by this migration
        op.drop_column("document_embeddings", "created_at")