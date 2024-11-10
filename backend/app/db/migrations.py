# backend/app/db/migrations.py
import os
import importlib
import pkgutil
from alembic import command
from alembic.config import Config
from alembic.script import ScriptDirectory
from alembic.runtime.environment import EnvironmentContext

def get_alembic_config():
    """Get Alembic configuration."""
    config = Config()
    config.set_main_option("script_location", "migrations")
    config.set_main_option("sqlalchemy.url", os.getenv("DATABASE_URL", "sqlite:///./data/secure_cms.db"))
    return config

def create_migration(message):
    """Create a new migration."""
    config = get_alembic_config()
    command.revision(config, message=message, autogenerate=True)

def upgrade_database():
    """Upgrade database to latest version."""
    config = get_alembic_config()
    command.upgrade(config, "head")

def downgrade_database(revision):
    """Downgrade database to specific revision."""
    config = get_alembic_config()
    command.downgrade(config, revision)

def get_current_revision():
    """Get current database revision."""
    config = get_alembic_config()
    script = ScriptDirectory.from_config(config)
    
    def get_revision(rev, context):
        return rev
    
    with EnvironmentContext(config, script, fn=get_revision) as env:
        return env.get_head_revision()

# Migration templates
MIGRATION_TEMPLATE = """"""\"
${message}

Revision ID: ${up_revision}
Revises: ${down_revision}
Create Date: ${create_date}

\"""
from alembic import op
import sqlalchemy as sa
${imports if imports else ""}

# revision identifiers, used by Alembic.
revision = ${repr(up_revision)}
down_revision = ${repr(down_revision)}
branch_labels = ${repr(branch_labels)}
depends_on = ${repr(depends_on)}

def upgrade():
    ${upgrades if upgrades else "pass"}

def downgrade():
    ${downgrades if downgrades else "pass"}
"""
