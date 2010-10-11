# -*- coding: iso-8859-1 -*-

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

from pytrainer.lib.ddbb import DDBB
from pytrainer.lib.graphdata import GraphData

class Athlete:
    def __init__(self, data_path = None, parent = None):
        logging.debug('>>')
        self.parent = parent
        self.pytrainer_main = parent
        self.data_path = data_path
        self.init_from_conf()
        self.data = self.get_athlete_stats()
        self.graphdata = self.get_athlete_data()
        logging.debug('<<')
        
    def refresh(self):
        self.init_from_conf()
        self.data = self.get_athlete_stats()
        self.graphdata = self.get_athlete_data()
        
    def init_from_conf(self):
        logging.debug('>>')
        self.name = self.pytrainer_main.profile.getValue("pytraining","prf_name")
        self.age = self.pytrainer_main.profile.getValue("pytraining","prf_age")
        self.height = self.pytrainer_main.profile.getValue("pytraining","prf_height")
        if self.pytrainer_main.profile.getValue("pytraining","prf_us_system") == "True":
            self.us_system = True
        else:
            self.us_system = False
        if self.us_system:
            self.weight_unit = _("lb")
        else:
            self.weight_unit = _("kg")
        logging.debug('<<')
        
    def get_athlete_stats(self):
        logging.debug('>>')
        stats = []
        results = self.pytrainer_main.ddbb.select("athletestats", "id_athletestat, date, weight, bodyfat, restinghr, maxhr", mod="order by date")
        logging.debug('Found %d athlete stats results' % len(results))
        for row in results:
            date = dateutil.parser.parse(row[1]).date()
            stats.append({'id_athletestat': row[0], 'Date': row[1], 'Weight':row[2], 'BF': row[3], 'RestingHR':row[4], 'MaxHR':row[5]})        
        logging.debug('<<')
        return stats
        
    def get_athlete_data(self):
        logging.debug('>>')
        graphdata = {}
        graphdata['weight'] = GraphData(title="Weight", xlabel="Date", ylabel="Weight (%s)" % (self.weight_unit))
        graphdata['weight'].set_color('#3300FF', '#3300FF')
        #graphdata['weight'].graphType = 'fill'
        graphdata['bf'] = GraphData(title="Body Fat", xlabel="Date", ylabel="Body Fat (%s)" % (self.weight_unit))
        graphdata['bf'].set_color('#FF6600', '#FF6600')
        #graphdata['bf'].graphType = 'fill'
        graphdata['restinghr'] = GraphData(title="Resting Heartrate", xlabel="Date", ylabel="Resting Heartrate (bpm)")
        graphdata['restinghr'].set_color('#660000', '#660000')
        graphdata['restinghr'].show_on_y2 = True
        graphdata['maxhr'] = GraphData(title="Maximum Heartrate", xlabel="Date", ylabel="Maximum Heartrate (bpm)")
        graphdata['maxhr'].set_color('#33CC99', '#33CC99')
        graphdata['maxhr'].show_on_y2 = True
        for row in self.data:
            date = dateutil.parser.parse(row['Date']).date()
            if row['Weight']:
                weight = float(row['Weight'])
            else:
                weight = None
            if row['BF']:
                bf = float(row['BF']) / 100 * weight
            else:
                bf = None
            graphdata['weight'].addPoints(x=date, y=weight)
            graphdata['bf'].addPoints(x=date, y=bf)
            graphdata['restinghr'].addPoints(x=date, y=row['RestingHR'])
            graphdata['maxhr'].addPoints(x=date, y=row['MaxHR'])
        return graphdata
        
        
    def update_athlete_stats(self, id_athletestat, date, weight, bodyfat, restinghr, maxhr):
        logging.debug('>>')
        try:
            date = dateutil.parser.parse(date).date()
        except ValueError:
            return
        cells = "date, weight, bodyfat, restinghr, maxhr"
        values = (date, weight, bodyfat, restinghr, maxhr)
        #Update database
        self.pytrainer_main.ddbb.update("athletestats",cells,values," id_athletestat=%d" %int(id_athletestat))
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
            return
        cells = "date, weight, bodyfat, restinghr, maxhr"
        values = (date, weight, bodyfat, restinghr, maxhr)
        #Update DB
        self.pytrainer_main.ddbb.insert("athletestats",cells,values)
        logging.debug('<<')
