"""Initial migration

Revision ID: 001
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Create users table
    op.create_table('users',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('username', sa.String(), nullable=True),
        sa.Column('full_name', sa.String(), nullable=True),
        sa.Column('auth_provider', sa.String(), nullable=True),
        sa.Column('auth_provider_id', sa.String(), nullable=True),
        sa.Column('role', sa.String(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('is_verified', sa.Boolean(), nullable=True),
        sa.Column('stripe_customer_id', sa.String(), nullable=True),
        sa.Column('subscription_tier', sa.String(), nullable=True),
        sa.Column('credits_remaining', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('last_login', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email'),
        sa.UniqueConstraint('username')
    )
    
    # Create audio_jobs table
    op.create_table('audio_jobs',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=True),
        sa.Column('filename', sa.String(), nullable=True),
        sa.Column('source_url', sa.String(), nullable=True),
        sa.Column('file_size', sa.Integer(), nullable=True),
        sa.Column('file_url', sa.String(), nullable=True),
        sa.Column('processed_file_url', sa.String(), nullable=True),
        sa.Column('rights_confirmed', sa.Boolean(), nullable=True),
        sa.Column('metadata_only', sa.Boolean(), nullable=True),
        sa.Column('consent_timestamp', sa.DateTime(), nullable=True),
        sa.Column('status', sa.String(), nullable=True),
        sa.Column('progress', sa.Float(), nullable=True),
        sa.Column('status_message', sa.Text(), nullable=True),
        sa.Column('features', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create generations table
    op.create_table('generations',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=True),
        sa.Column('job_id', sa.String(), nullable=False),
        sa.Column('genre', sa.String(), nullable=False),
        sa.Column('mood', sa.String(), nullable=False),
        sa.Column('explicit', sa.Boolean(), nullable=True),
        sa.Column('language', sa.String(), nullable=True),
        sa.Column('rhyme_scheme', sa.String(), nullable=True),
        sa.Column('syllables_per_beat', sa.Float(), nullable=True),
        sa.Column('target_structure', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('status', sa.String(), nullable=True),
        sa.Column('progress', sa.Float(), nullable=True),
        sa.Column('status_message', sa.Text(), nullable=True),
        sa.Column('lyrics_json', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('title', sa.String(), nullable=True),
        sa.Column('estimated_syllables', sa.Integer(), nullable=True),
        sa.Column('rhyme_accuracy', sa.Float(), nullable=True),
        sa.Column('syllable_accuracy', sa.Float(), nullable=True),
        sa.Column('structure_match', sa.Float(), nullable=True),
        sa.Column('lrc_url', sa.String(), nullable=True),
        sa.Column('srt_url', sa.String(), nullable=True),
        sa.Column('txt_url', sa.String(), nullable=True),
        sa.Column('pdf_url', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['job_id'], ['audio_jobs.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create feedback table
    op.create_table('feedback',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=True),
        sa.Column('generation_id', sa.String(), nullable=False),
        sa.Column('type', sa.String(), nullable=False),
        sa.Column('rating', sa.Integer(), nullable=True),
        sa.Column('comment', sa.Text(), nullable=True),
        sa.Column('edits', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('user_agent', sa.String(), nullable=True),
        sa.Column('ip_address', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['generation_id'], ['generations.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

def downgrade() -> None:
    op.drop_table('feedback')
    op.drop_table('generations')
    op.drop_table('audio_jobs')
    op.drop_table('users')
