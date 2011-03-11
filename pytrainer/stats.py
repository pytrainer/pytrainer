# -*- coding: iso-8859-1 -*-

#Copyright (C) Sigurður H. Pálsson shp@itn.is

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

class Stats:
    def __init__(self, data_path = None, parent = None):
        logging.debug('>>')
        self.parent = parent
        self.pytrainer_main = parent
        self.data_path = data_path
        self.init_from_conf()
        self.data = self.get_stats()
        logging.debug('<<')

    def refresh(self):
        self.init_from_conf()
        self.data = self.get_stats()

    def init_from_conf(self):
        logging.debug('>>')
        logging.debug('<<')

    def get_stats(self):
        logging.debug('>>')
        data = {
            'sports' : {},
            'total_duration' : 0,
            'total_distance' : 0,
        }
        
        fields = ['maxspeed', 'maxbeats', 'duration', 'distance']
        data['fields'] = fields
        
        for f in fields:
            data[f] = 0
        
        sports = dict([(s['id_sports'], s['name']) for s in self.pytrainer_main.ddbb.select_dict("sports", ('id_sports', 'name'))])
        results = self.pytrainer_main.ddbb.select_dict("records", ('id_record', 'date', 'sport', 'distance', 'duration', 'maxbeats', 'maxspeed', 'maxpace', 'average'))
        for r in results:
#            r['duration'] /= 3600
            if r['sport'] not in data['sports']:
                data['sports'][r['sport']] = {'name': sports[r['sport']]}
                for f in fields:
                    data['sports'][r['sport']][f] = 0
                    data['sports'][r['sport']]['total_'+f] = 0
            for f in fields:
                data['sports'][r['sport']][f] = max(data['sports'][r['sport']][f], r[f])
                if r[f] is not None:
                    data['sports'][r['sport']]['total_'+f] += r[f]
                    data[f] = max(data[f], r[f])
                else:
                    logging.info('Skipping null values')
                
                
            data['total_duration'] += r['duration']
            data['total_distance'] += r['distance']
            
            if not 'start_date' in data: data['start_date'] = r['date']
            data['start_date'] = min(data['start_date'], r['date'])
            if not 'end_date' in data: data['end_date'] = r['date']
            data['end_date'] = max(data['end_date'], r['date'])
            
        logging.debug('<<')
        return data

