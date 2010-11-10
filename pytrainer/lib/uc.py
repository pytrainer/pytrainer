# -*- coding: iso-8859-1 -*-

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

from pytrainer.lib.singleton import Singleton

""" Units of physical quantities [metric, imperial] """
uc_units = {'distance' : ['km','mi'] , 'speed' : ['km/h', 'mph'], 
            'pace' : ['min/km','min/mi'], 'height' : ['m', 'ft'],
            'weight': ['kg', 'lb']}

""" Conversion factors from metric to imperial, units as in uc_units """ 
uc_factors = {'distance' : 0.621371192, 'speed': 0.621371192, 'pace':1.609344, 
              'height': 3.2808399, 'weight': 2.204624}

class UC(Singleton):
    """ 
    When instantiated first time us is assigned, otherwise not.
    Can be called with or w/o argument.
      us = False; metric system
      us = True ; imperial system
    """
    def __init__(self, *args):
        _us = False
        if args:
            if args[0] in [True, False]:
                _us = args[0]
        if not hasattr(self, 'us'):
            self.us = _us
            
    def __str__(self):
        if self.us:
            return 'imperial'
        else:
            return 'metric'
        
    def set_us(self, us):
        self.us = us
        
    def get_unit(self, quantity):
        if self.us:
            return uc_units[quantity][1]
        else:
            return uc_units[quantity][0]
            
    unit_distance = property(lambda self: self.get_unit('distance') )      
    unit_speed = property( lambda self: self.get_unit('speed') ) 
    unit_pace = property( lambda self: self.get_unit('pace') )     
    unit_height = property( lambda self: self.get_unit('height') )  
    unit_weight = property( lambda self: self.get_unit('weight') )        
    
    def sys2usr(self, quantity, value):
        """gives value of physical quantity (metric) in users system"""        
        if self.us:
            return value * uc_factors[quantity]
        else:
            return value 
   
    def usr2sys(self, quantity, value):
        """takes value (users system) and convert to metric (sys)"""        
        if self.us:
            return value / uc_factors[quantity]    
        else:
            return value   
            
