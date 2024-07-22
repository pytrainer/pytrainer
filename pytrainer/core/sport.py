# -*- coding: utf-8 -*-

#Copyright (C) Nathan Jones ncjones@users.sourceforge.net

#This program is free software; you can redistribute it and/or
#modify it under the terms of the GNU General Public License
#as published by the Free Software Foundation; either version 2
#of the License, or (at your option) any later version.

#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.

#You should have received a copy of the GNU General Public License
#along with this program; if not, write to the Free Software
#Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.

from pytrainer.util.color import Color, color_from_hex_string
from pytrainer.lib.ddbb import DeclarativeBase, ForcedInteger
from sqlalchemy import Column, Integer, Float, Unicode, CheckConstraint, select
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.exc import InvalidRequestError, IntegrityError, StatementError
import sqlalchemy.types as types
import logging

class ColorType(types.TypeDecorator):
    """Sqlalchemy type to convert between CHAR and the Color object"""

    impl = types.CHAR

    def process_bind_param(self, value, dialect):
        return value.to_hex_string()

    def process_result_value(self, value, dialect):
        return color_from_hex_string(value)

class Sport(DeclarativeBase):
    """A type of exercise. For example: "running" or "cycling"."""

    __tablename__ = 'sports'
    color = Column(ColorType(length=6), nullable=False)
    id = Column('id_sports', Integer, primary_key=True, nullable=False)
    max_pace = Column(ForcedInteger, CheckConstraint('max_pace>=0'))
    met = Column(Float, CheckConstraint('met>=0'))
    name = Column(Unicode(length=100), nullable=False, unique=True, index=True)
    weight = Column(Float, CheckConstraint('weight>=0'), nullable=False)

    def __init__(self, **kwargs):
        self.name = u""
        self.weight = 0.0
        self.met = None
        self.max_pace = None
        self.color = Color(0x0000ff)
        super(Sport, self).__init__(**kwargs)

class SportServiceException(Exception):

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)

class SportService:
    """Provides access to stored sports."""

    def __init__(self, ddbb):
        self._ddbb = ddbb

    def get_sport(self, sport_id):
        """Get the sport with the specified id.

        If no sport with the given id exists then None is returned."""
        if sport_id is None:
            raise ValueError("Sport id cannot be None")
        stmt = select(Sport).where(Sport.id == sport_id)
        with self._ddbb.session as session:
            result = session.execute(stmt)
            try:
                return result.scalar_one()
            except NoResultFound:
                return None

    def get_sport_by_name(self, name):
        """Get the sport with the specified name.

        If no sport with the given name exists then None is returned."""
        if name is None:
            raise ValueError("Sport name cannot be None")
        stmt = select(Sport).where(Sport.name == name)
        with self._ddbb.session as session:
            result = session.execute(stmt)
            try:
                return result.scalar_one()
            except NoResultFound:
                return None

    def get_all_sports(self):
        """Get all stored sports."""
        stmt = select(Sport)
        with self._ddbb.session as session:
            result = session.execute(stmt)
            return result.scalars().all()

    def store_sport(self, sport):
        """Store a new or update an existing sport.

        The stored object is returned."""
        try:
            with self._ddbb.session as session:
                session.add(sport)
                session.commit()
                session.refresh(sport)
        except (IntegrityError, StatementError) as err:
            session.rollback()
            raise SportServiceException(str(err)) from err
        return sport

    def remove_sport(self, sport):
        """Delete a stored sport.

        All records associated with the sport will also be deleted."""
        if not sport.id:
            raise SportServiceException("Cannot remove sport which has not been stored: '{0}'.".format(sport.name))
        try:
            with self._ddbb.session as session:
                session.delete(sport)
                session.commit()
        except InvalidRequestError:
            raise SportServiceException("Sport id %s not found" % sport.id)
        logging.debug("Deleted sport: %s", sport.name)
