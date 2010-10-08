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

from lib.ddbb import DDBB

class Athlete:
    def __init__(self, data_path = None, parent = None):
        logging.debug('>>')
        self.parent = parent
        self.pytrainer_main = parent
        self.data_path = data_path
        logging.debug('<<')
        
    def get_athlete_stats(self):
        print('>>')
        stats = []
        results = self.pytrainer_main.ddbb.select("athletestats", "id_athletestat, date, weight, bodyfat, restinghr, maxhr")
        print('Found %d athlete stats results' % len(results))
        for row in results:
            stats.append({'id_athletestat': row[0], 'Date': row[1], 'Weight':row[2], 'BF': row[3], 'RestingHR':row[4], 'MaxHR':row[5]})        
        return stats
        print('<<')
        
        
