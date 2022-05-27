"""Adding copy request tables

Revision ID: 396048c16b59
Revises:
Create Date: 2022-05-12 14:29:15.227461

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '396048c16b59'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('approval_request',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('status', sa.String(), nullable=True),
    sa.Column('submitted_by', sa.String(), nullable=True),
    sa.Column('submitted_at', sa.DateTime(), nullable=True),
    sa.Column('destination_id', postgresql.UUID(as_uuid=True), nullable=True),
    sa.Column('source_id', postgresql.UUID(as_uuid=True), nullable=True),
    sa.Column('note', sa.String(), nullable=True),
    sa.Column('project_code', sa.String(), nullable=True),
    sa.Column('destination_path', sa.String(), nullable=True),
    sa.Column('source_path', sa.String(), nullable=True),
    sa.Column('review_notes', sa.String(), nullable=True),
    sa.Column('completed_by', sa.String(), nullable=True),
    sa.Column('completed_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id'),
    schema='pilot_approval'
    )
    op.create_table('approval_entity',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('request_id', postgresql.UUID(as_uuid=True), nullable=True),
    sa.Column('entity_id', postgresql.UUID(as_uuid=True), nullable=True),
    sa.Column('entity_type', sa.String(), nullable=True),
    sa.Column('review_status', sa.String(), nullable=True),
    sa.Column('reviewed_by', sa.String(), nullable=True),
    sa.Column('reviewed_at', sa.String(), nullable=True),
    sa.Column('parent_id', postgresql.UUID(as_uuid=True), nullable=True),
    sa.Column('copy_status', sa.String(), nullable=True),
    sa.Column('name', sa.String(), nullable=True),
    sa.Column('uploaded_by', sa.String(), nullable=True),,
    sa.Column('uploaded_at', sa.DateTime(), nullable=True),
    sa.Column('file_size', sa.BigInteger(), nullable=True),
    sa.ForeignKeyConstraint(['request_id'], ['pilot_approval.approval_request.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id'),
    schema='pilot_approval'
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('approval_entity', schema='pilot_approval')
    op.drop_table('approval_request', schema='pilot_approval')
    # ### end Alembic commands ###
