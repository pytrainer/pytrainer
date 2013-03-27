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
uc_units = {'distance' : [_('km'),_('mi')] , 'speed' : [_('km/h'), _('mph')], 
            'pace' : [_('min/km'),_('min/mi')], 'height' : [_('m'), _('ft')],
            'weight': [_('kg'), _('lb')]}

""" Conversion factors from metric to imperial, units as in uc_units """ 
uc_factors = {'distance' : 0.621371192, 'speed': 0.621371192, 'pace':1.609344, 
              'height': 3.2808399, 'weight': 2.204624}

def pace2float(pace_str):
    if pace_str.count(':') != 1:
        return 0.0
    else:
        _prts = pace_str.split(':')
        try:
            _p_min = int(_prts[0])
            _p_sec = int(_prts[1])
            return float( _p_min + (_p_sec/60.0))                   
        except:
            return 0.0

def float2pace(pace_flt):
    try:
        _pace = float(pace_flt)
    except:
        return ""
    _p_int = int(_pace)
    _p_frc = round((_pace - _p_int) * 60.0)
    if _p_frc == 60:
        _p_int += 1
        _p_frc = 0
    _pace_str = "%d:%02d" % (_p_int, _p_frc)  
    return _pace_str

class UC(Singleton):
    """ 
    When instantiated first time us is assigned to False.
      us = False; user system is metric
      us = True ; user system is imperial
    """
    def __init__(self):
        if not hasattr(self, 'us'):
            self.us = False
            
    def __str__(self):
        if self.us:
            return 'imperial'
        else:
            return 'metric'
        
    def set_us(self, us):
        if type(us) == bool:
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
        """ Gives value of physical quantity (metric) in users system"""
        try:
            _val = float(value)
        except (ValueError, TypeError):
            return None
        if self.us:
            return _val * uc_factors[quantity]
        else:
            return _val 
   
    def usr2sys(self, quantity, value):
        """ Takes value (users system) and convert to metric (sys)"""
        try:
            _val = float(value)
        except (ValueError, TypeError):
            return None        
        if self.us:
            return _val / uc_factors[quantity]    
        else:
            return _val

    def usr2sys_str(self, quantity, val_str):
        """ Similar to usr2sys but I/O is string representing a float.
            Necessary until we have proper input validation in windowrecord.
            Escpecially pace fix here should be eliminated asap. 
        """
        if not self.us:
            return val_str
            
        if quantity == 'pace':
            _pace_dec = pace2float(val_str)
            _pace_uc = self.usr2sys('pace', _pace_dec)
            return float2pace(_pace_uc)
        else:
            try:
                _val = float(val_str)
            except (ValueError, TypeError):
                return ""
            return str( self.usr2sys(quantity, _val))
    

    """ Aliases for sys2usr """         
    def distance(self, value):
        return self.sys2usr('distance', value)
    def speed(self, value):
        return self.sys2usr('speed', value)
    def pace(self, value):
        return self.sys2usr('pace', value)
    def height(self, value):
        return self.sys2usr('height', value)
    def weight(self, value):
        return self.sys2usr('weight', value)              
