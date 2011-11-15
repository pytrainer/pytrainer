from pytrainer.upgrade.context import UPGRADE_CONTEXT
import pytrainer.upgrade.versions.version014 as version14
import sqlalchemy

def upgrade(migrate_engine=None):
    if migrate_engine is None:
        # sqlalchemy-migrate 0.5.4 does not provide migrate engine to upgrade scripts
        migrate_engine = sqlalchemy.create_engine(UPGRADE_CONTEXT.db_url)
    version14.upgrade(migrate_engine)