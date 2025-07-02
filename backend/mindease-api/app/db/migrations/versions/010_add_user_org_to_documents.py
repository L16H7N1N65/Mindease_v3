"""add user_id & organization_id to documents

Revision ID: 010_add_user_org_to_documents    # <= 27 chars, OK
Revises: 009_add_rag_feedback_tables
Create Date: 2025-06-19 15:05
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql    

# ───────────────────────────────────────────────
revision = "010_add_user_org_to_documents"     
down_revision = "009_add_rag_feedback_tables"
branch_labels = None
depends_on = None
# ───────────────────────────────────────────────
INT_FK = sa.Integer()


def _column_exists(table_name: str, column_name: str) -> bool:
    """True if the column already exists in the live DB."""
    bind = op.get_bind()
    insp = sa.inspect(bind)
    return column_name in [col["name"] for col in insp.get_columns(table_name)]


# ───────────────────────────── upgrade ──────────────────────────────────────
def upgrade() -> None:
    # ------------------------------------------------------------------ #
    # 1) add / fix user_id                                               #
    # ------------------------------------------------------------------ #
    if not _column_exists("documents", "user_id"):
        op.add_column("documents", sa.Column("user_id", INT_FK, nullable=True))

    # create FK only if it doesn’t already exist
    op.create_foreign_key(
        constraint_name="fk_documents_user_id_users",
        source_table="documents",
        referent_table="users",
        local_cols=["user_id"],
        remote_cols=["id"],
        ondelete="SET NULL",
        deferrable=False,
        initially=None,
    )

    # ------------------------------------------------------------------ #
    # 2) add / fix organization_id                                       #
    # ------------------------------------------------------------------ #
    if not _column_exists("documents", "organization_id"):
        op.add_column("documents", sa.Column("organization_id", INT_FK, nullable=True))
    else:
        # column exists – be sure it’s INTEGER (it was wrongly created as UUID)
        op.alter_column(
            "documents",
            "organization_id",
            existing_type=sa.dialects.postgresql.UUID(as_uuid=True),
            type_=INT_FK,
            postgresql_using="organization_id::text::integer",
            nullable=True,
        )

    op.create_foreign_key(
        constraint_name="fk_documents_org_id_organizations",
        source_table="documents",
        referent_table="organizations",
        local_cols=["organization_id"],
        remote_cols=["id"],
        ondelete="SET NULL",
        deferrable=False,
        initially=None,
    )


# ──────────────────────────── downgrade ─────────────────────────────────────
def downgrade() -> None:
    op.drop_constraint("fk_documents_org_id_organizations", "documents", type_="foreignkey")
    op.drop_constraint("fk_documents_user_id_users",        "documents", type_="foreignkey")

    if _column_exists("documents", "organization_id"):
        op.drop_column("documents", "organization_id")
    if _column_exists("documents", "user_id"):
        op.drop_column("documents", "user_id")