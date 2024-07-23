# -*- coding: utf-8 -*-

#Copyright (C) Fiz Vazquez vud1@sindominio.net
#Modified by dgranda

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

import logging
import dateutil

from pytrainer.lib.ddbb import DeclarativeBase, ForcedInteger
from pytrainer.lib.uc import UC
from sqlalchemy import Column, Float, Date, Integer, select, delete, update
from sqlalchemy.orm import Session

class Athletestat(DeclarativeBase):
    __tablename__ = 'athletestats'
    bodyfat = Column(Float)
    date = Column(Date)
    id_athletestat = Column(Integer, primary_key=True)
    maxhr = Column(ForcedInteger)
    restinghr = Column(ForcedInteger)
    weight = Column(Float)

class Athlete:
    def __init__(self, data_path = None, parent = None):
        self.parent = parent
        self.pytrainer_main = parent
        self.data_path = data_path
        self.uc = UC()

    def refresh(self):
        logging.debug('>>')
        self.init_from_conf()
        self.data = self.get_athlete_stats()
        self.graphdata = self.get_athlete_data()
        logging.debug('<<')

    def init_from_conf(self):
        logging.debug('>>')
        self.name = self.pytrainer_main.profile.getValue("pytraining","prf_name")
        self.age = self.pytrainer_main.profile.getValue("pytraining","prf_age")
        self.height = self.pytrainer_main.profile.getValue("pytraining","prf_height")
        logging.debug('<<')

    def get_athlete_stats(self):
        logging.debug('>>')
        ret = []
        stmt = select(Athletestat).order_by(Athletestat.date)
        with Session(self.pytrainer_main.ddbb.engine) as session:
            for stat in session.execute(stmt).scalars().all():
                d = dict(stat.__dict__)
                d.pop('_sa_instance_state', None)
                ret.append(d)
        return ret

    def get_athlete_data(self):
        from pytrainer.lib.graphdata import GraphData
        logging.debug('>>')
        graphdata = {}
        graphdata['weight'] = GraphData(title="Weight", xlabel="Date", ylabel="Weight (%s)" % (self.uc.unit_weight))
        graphdata['weight'].set_color('#3300FF', '#3300FF')
        #graphdata['weight'].graphType = 'date'
        graphdata['bodyfat'] = GraphData(title="Body Fat", xlabel="Date", ylabel="Body Fat (%)")
        graphdata['bodyfat'].set_color('#FF6600', '#FF6600')
        #graphdata['bf'].graphType = 'date'
        graphdata['restinghr'] = GraphData(title="Resting Heartrate", xlabel="Date", ylabel="Resting Heartrate (bpm)")
        graphdata['restinghr'].set_color('#660000', '#660000')
        graphdata['restinghr'].show_on_y2 = True
        graphdata['maxhr'] = GraphData(title="Maximum Heartrate", xlabel="Date", ylabel="Maximum Heartrate (bpm)")
        graphdata['maxhr'].set_color('#33CC99', '#33CC99')
        graphdata['maxhr'].show_on_y2 = True
        for row in self.data:
            if not 'date' in row or not row['date']:
                continue
            else:
                date = row['date']
            if 'weight' in row and row['weight']:
                weight = float(row['weight'])
            else:
                weight = ""
            if 'bodyfat' in row and row['bodyfat'] and weight:
                bf = float(row['bodyfat']) / 100 * weight
            else:
                bf = ""
            graphdata['weight'].addPoints(x=date, y=weight)
            graphdata['bodyfat'].addPoints(x=date, y=bf)
            graphdata['restinghr'].addPoints(x=date, y=row['restinghr'])
            graphdata['maxhr'].addPoints(x=date, y=row['maxhr'])
        #Remove empty data
        for item in list(graphdata.keys()):
            if len(graphdata[item]) == 0:
                logging.debug( "No values for %s. Removing...." % item )
                del graphdata[item]
        return graphdata


    def update_athlete_stats(self, id_athletestat, date, weight, bodyfat, restinghr, maxhr):
        logging.debug('>>')
        try:
            date = dateutil.parser.parse(date).date()
            logging.debug("update_athlete_stats called with invalid date")
            logging.debug('!<<')
        except ValueError:
            return
        #Update DB
        with Session(self.pytrainer_main.ddbb.engine) as session:
            stmt = select(Athletestat).filter_by(id_athletestat=id_athletestat)
            data = session.execute(stmt).scalar_one()
            data.date = date
            data.weight = weight
            data.bodyfat = bodyfat
            data.restinghr = restinghr
            data.maxhr = maxhr
            session.commit()
        logging.debug('<<')

    def insert_athlete_stats(self, date, weight, bodyfat, restinghr, maxhr):
        logging.debug('>>')
        if not date and not weight and not bodyfat and not restinghr and not maxhr:
            #no data supplied
            logging.debug("insert_athlete_stats called with no data")
            logging.debug('!<<')
            return
        try:
            date = dateutil.parser.parse(date).date()
        except ValueError:
            logging.debug("insert_athlete_stats called with invalid date")
            logging.debug('!<<')
            return
        #Update DB
        data = Athletestat(date=date, weight=weight, bodyfat=bodyfat, restinghr=restinghr, maxhr=maxhr)
        with Session(self.pytrainer_main.ddbb.engine) as session:
            session.add(data)
            session.commit()
        logging.debug('<<')

    def delete_record(self, data):
        logging.debug('>>')
        with Session(self.pytrainer_main.ddbb.engine) as session:
            stmt = delete(Athletestat).where(Athletestat.id_athletestat == int(data))
            session.execute(stmt)
            session.commit()
        logging.debug('<<')
