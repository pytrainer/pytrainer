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

class Stats:
    def __init__(self, sport_service, parent = None):
        logging.debug('>>')
        self._sport_service = sport_service
        self.pytrainer_main = parent
        logging.debug('<<')

    def refresh(self):
        self.data = self.get_stats()

    def get_stats(self):
        logging.debug('>>')
        data = {
            'sports' : {},
            'total_duration' : 0,
            'total_distance' : 0,
        }
        
        fields = ['maxspeed', 'beats', 'maxbeats', 'duration', 'distance']
        data['fields'] = fields
        
        for f in fields:
            data[f] = 0
        
        results = self.pytrainer_main.ddbb.select_dict("records", ('id_record', 'date', 'sport', 'distance', 'duration', 'maxbeats', 'maxspeed', 'maxpace', 'average','pace','beats'))
        for r in results:
            if r['sport'] is None or r['sport'] is 0:
                # temporary fix to ignore corrupt records caused by GPX import bug
                continue
            if r['sport'] not in data['sports']:
                sport = self._sport_service.get_sport(r['sport'])
                data['sports'][r['sport']] = {'name': sport.name, 'count': 0}
                for f in fields:
                    data['sports'][r['sport']][f] = 0
                    data['sports'][r['sport']]['total_'+f] = 0
            data['sports'][r['sport']]['count'] += 1
            for f in fields:
                data['sports'][r['sport']][f] = max(data['sports'][r['sport']][f], r[f])
                if r[f] is not None:
                    data['sports'][r['sport']]['total_'+f] += r[f]
                    data[f] = max(data[f], r[f])
                else:
                    logging.info('Skipping null values')
                    
            if 'avg_hr' not in data['sports'][r['sport']]:
                data['sports'][r['sport']]['avg_hr'] = [0, 0]
            if r['beats']:
                data['sports'][r['sport']]['avg_hr'][0] += 1
                data['sports'][r['sport']]['avg_hr'][1] += r['beats']
                
            data['total_duration'] += r['duration']
            data['total_distance'] += r['distance']
            
            if not r['maxspeed'] and r['duration']:
                data['sports'][r['sport']]['maxspeed'] = max(data['sports'][r['sport']]['maxspeed'], r['distance'] / r['duration'] * 3600)
            
            if not 'start_date' in data: data['start_date'] = r['date']
            data['start_date'] = min(data['start_date'], r['date'])
            if not 'end_date' in data: data['end_date'] = r['date']
            data['end_date'] = max(data['end_date'], r['date'])
            
        for s in data['sports']:
            if data['sports'][s]['avg_hr'][0]:
                data['sports'][s]['avg_hr'] = int(data['sports'][s]['avg_hr'][1] / data['sports'][s]['avg_hr'][0])
            else:
                data['sports'][s]['avg_hr'] = None
            
        logging.debug('<<')
        return data

