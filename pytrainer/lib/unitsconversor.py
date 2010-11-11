# -*- coding: iso-8859-1 -*-

#Copyright (C) Fiz Vazquez vud1@sindominio.net

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

'''def _set_units(self):
    if self.us_system:
			self.distance_unit = _("miles")
			self.speed_unit = _("miles/h")
			self.pace_unit = _("min/mile")
			self.height_unit = _("feet")
    else:
			self.distance_unit = _("km")
			self.speed_unit = _("km/h")
			self.pace_unit = _("min/km")
			self.height_unit = _("m")
    self.units = { 'distance': self.distance_unit, 'average': self.speed_unit, 'upositive': self.height_unit, 'unegative': self.height_unit, 'maxspeed': self.speed_unit, 'pace': self.pace_unit, 'maxpace': self.pace_unit }'''

def km2miles(kilometers):
    try:
        km = float(kilometers)
        return km*0.621371192
    except Exception as e:
        return 0.0

def miles2mk(miles):
    try:
        m = float(miles)
        return m/0.621371192
    except Exception as e:
        return 0.0

def pacekm2miles(kilometers):
    try:
        km = float(kilometers)
        return km/0.621371192
    except Exception as e:
        return 0.0

def pacemiles2mk(miles):
    try:
        m = float(miles)
        return m*0.621371192
    except Exception as e:
        return 0.0

def m2feet(meter):
    try:
        m = float(meter)
        return m*3.2808399
    except Exception as e:
        return 0.0

def feet2m(feet):
    try:
        m = float(feet)
        return m/3.2808399
    except Exception as e:
        return 0.0

def kg2pound(kg):
    try:
        m = float(kg)
        return m*2.20462262
    except Exception as e:
        return 0.0

def pound2kg(pound):
    try:
        m = float(pound)
        return m/2.20462262
    except Exception as e:
        return 0.0

def myset_text(gtkentry, quantity, value, **kwargs):
    _us = False
    _round = False
    _value = value
    
    if kwargs.has_key('us'):
        if kwargs['us'] == True:
            _us = True
    if kwargs.has_key('units'):
        if kwargs['units']:
            _units = True
    if kwargs.has_key('round'):
        _round = True
        _round_digits = kwargs['round'] 
    
    print 'set_text via myset_text()'
    print quantity, _value
    # quantity=physical quantitiy like 'distance' or 'speed' 
    # here we should call the universal 'conversion prepare for output' filter
    # need the same for get_text
    try:
        _value = filter_inout(quantity, _value, 'out', us=_us, round=_round_digits)
        _value = str(_value)
    except:
        _value = ''
    gtkentry.set_text(_value)

def myget_text(gtkentry, quantity, **kwargs):
    _us = False
    _round = False
    _value = gtkentry.get_text()
    
    if kwargs.has_key('us'):
        if kwargs['us'] == True:
            _us = True
    if kwargs.has_key('units'):
        if kwargs['units']:
            _units = True
    if kwargs.has_key('round'):
        _round = True
        _round_digits = kwargs['round'] 

    _value = float(_value)
    _value = filter_inout(quantity, _value, 'in', us=_us)
    return float(_value)
    
def filter_inout(param, values, direction,**kwargs):
    """ """
    units = {'distance' : ['km','mi'] , 'speed' : ['km/h', 'mph'], 
         'pace' : ['min/km','min/mi'], 'height' : ['m', 'ft']}
         
    if direction == 'out':  #all comes from metric
        myexp = 1
    else:
        myexp = -1
    if not type(values) == list:
        _list = False    
        values_return = [values]
    else:
        _list = True
        values_return = values
    _units = False
    _round = False
    _round_digits = 99
    #print kwargs
    _us = False
    if kwargs.has_key('us'):
        if kwargs['us'] == True:
            _us = True
    if kwargs.has_key('units'):
        if kwargs['units']:
            _units = True
    if kwargs.has_key('round'):
        _round = True
        _round_digits = kwargs['round']   
                                                            
    if _us: #if us:
        if param in ['distance', 'speed']:    
            values_return = [x * (0.6213711**myexp) for x in values_return]
        elif param in ['pace']:
            values_return = [x * (1.609344**myexp) for x in values_return]    
        elif param in ['height']:
            values_return = [x * (3.2808399**myexp) for x in values_return] 
               
    if _round:
        values_return = [round(x, _round_digits) for x in values_return]  
                   
    if _units:
        if _us:
          values_return = [str(x) + ' ' + units[param][1] for x in values_return]
        else:
          values_return = [str(x) + ' ' + units[param][0] for x in values_return]

    if not _list:
        return values_return[0] 
    else:       
        return values_return
