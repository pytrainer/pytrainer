# -*- coding: utf-8 -*-

# Copyright (C) Nathan Jones ncjones@users.sourceforge.net
# Copyright (C) Arto Jantunen <viiru@iki.fi>

# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.

import sqlalchemy
from sqlalchemy.exc import NoSuchTableError, OperationalError
from sqlalchemy.sql.expression import func
from sqlalchemy.schema import MetaData

from pytrainer.lib.ddbb import DeclarativeBase


class MigrateVersion(DeclarativeBase):
    __tablename__ = 'migrate_version'

    repository_id = sqlalchemy.Column(sqlalchemy.String(250), primary_key=True)
    repository_path = sqlalchemy.Column(sqlalchemy.Text)
    version = sqlalchemy.Column(sqlalchemy.Integer)


class MigratableDb:
    """Tool to check and return database version."""

    def __init__(self, ddbb):
        """Create a migratable DB.

        Arguments:
        repository_path -- The path to the migrate repository, relative to the
            pypath.
        db_url -- the connection URL string for the DB.
        """
        self.ddbb = ddbb

    def is_empty(self):
        """Check if the DB schema is empty.

        An empty schema indicates a new uninitialised database."""
        metadata = MetaData()
        metadata.reflect(bind=self.ddbb.engine)
        tables = metadata.tables
        return not tables

    def is_versioned(self):
        """ Check if the DB has been initiaized with version metadata."""
        try:
            self.get_version()
        except OperationalError:
            return False
        except NoSuchTableError:
            return False
        return True

    def get_version(self):
        """Get the current version of the versioned DB.

        Raises OperationError if the DB is not initialized."""
        latest = self.ddbb.session.query(func.max(MigrateVersion.version)).one()
        return latest[0]

    def get_upgrade_version(self):
        """Get the latest version available in upgrade repository."""
        return 15

    def version(self, initial_version):
        """Initialize the database with migrate metadata.

        Raises DatabaseAlreadyControlledError if the DB is already initialized."""
        self.ddbb.session.add(
            MigrateVersion(
                repository_id='pytrainer',
                repository_path='/usr/lib/python3/site-packages/pytrainer/upgrade',
                version=15,
                )
            )
        self.ddbb.session.commit()

    def upgrade(self):
        """Run all available upgrade scripts for the repository."""
        from pytrainer.gui.dialogs import warning_dialog
        current_version = self.get_version()
        warning_dialog(
            title="Database migration not supported",
            text=f"Migrating from database version {current_version} not supported. \
Please use pytrainer version 2.1.0 to migrate the database.",
        )
        exit(1)
