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
