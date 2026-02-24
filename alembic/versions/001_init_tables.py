from alembic import op
import sqlalchemy as sa

revision = '001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    role_enum = sa.Enum('ADMIN', 'DEVELOPER', 'USER', name='roleenum')
    stage_enum = sa.Enum('NONE', 'STAGE', 'PROD', 'AB', 'ARCHIVED', name='stageenum')

    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('hashed_password', sa.String(), nullable=False),
        sa.Column('role', role_enum, nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)

    op.create_table(
        'registered_models',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_registered_models_id'), 'registered_models', ['id'], unique=False)
    op.create_index(op.f('ix_registered_models_name'), 'registered_models', ['name'], unique=True)

    op.create_table(
        'model_versions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('model_id', sa.Integer(), nullable=False),
        sa.Column('version_number', sa.Integer(), nullable=False),
        sa.Column('created_by_id', sa.Integer(), nullable=False),
        sa.Column('source', sa.String(), nullable=True),
        sa.Column('dataset_reference', sa.String(), nullable=True),
        sa.Column('current_stage', stage_enum, nullable=True),
        sa.Column('s3_artifact_uri', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['created_by_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['model_id'], ['registered_models.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_model_versions_id'), 'model_versions', ['id'], unique=False)

    op.create_table(
        'model_metrics',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('version_id', sa.Integer(), nullable=False),
        sa.Column('key', sa.String(), nullable=False),
        sa.Column('value', sa.Float(), nullable=False),
        sa.ForeignKeyConstraint(['version_id'], ['model_versions.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_model_metrics_id'), 'model_metrics', ['id'], unique=False)

    op.create_table(
        'model_parameters',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('version_id', sa.Integer(), nullable=False),
        sa.Column('key', sa.String(), nullable=False),
        sa.Column('value', sa.String(), nullable=False),
        sa.ForeignKeyConstraint(['version_id'], ['model_versions.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_model_parameters_id'), 'model_parameters', ['id'], unique=False)

    op.create_table(
        'state_transitions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('version_id', sa.Integer(), nullable=False),
        sa.Column('from_stage', sa.String(), nullable=False),
        sa.Column('to_stage', sa.String(), nullable=False),
        sa.Column('actor_id', sa.Integer(), nullable=False),
        sa.Column('reason', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['actor_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['version_id'], ['model_versions.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_state_transitions_id'), 'state_transitions', ['id'], unique=False)

def downgrade() -> None:
    op.drop_table('state_transitions')
    op.drop_table('model_parameters')
    op.drop_table('model_metrics')
    op.drop_table('model_versions')
    op.drop_table('registered_models')
    op.drop_table('users')
    sa.Enum(name='stageenum').drop(op.get_bind(), checkfirst=False)
    sa.Enum(name='roleenum').drop(op.get_bind(), checkfirst=False)