#!/usr/bin/python
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

from optparse import OptionParser
import os

#Fijate, primero cogemos las variables que nos son mandadas desde la
#configuracion del plugin. En este caso "nikeid". 
parser = OptionParser()
parser.add_option("-n", "--nikeid", dest="nikeid")
(options,args) =  parser.parse_args()
nikeid = options.nikeid

#Por aqui deberias meter tu codigo que accede al ipod y coge los datos que 
#necesitas. Estas variables que yo meto a mano deberian salir del xml de tu ipod.

import SOAPpy
server = SOAPpy.SOAPProxy("http://localhost:8081/")
title="Un titulo"
distance="23.3" # Ojo, distance en km
time="3445" #Tiempo en segundos
upositive=None #Nivel acumulado positivo, dejalo en nada
unegative=None #Nivel acumulado negativo, dejalo en nada
bpm=None #Es la media de pulsaciones.. como no tienes pulsometro, dejalo en nada
calories="987" #numero de calorias
date="2007-09-10" #fecha en formato ingles
comments=None
#ahora metemos los datos a traves del webservice y recogemos la variable que nos pasa el server.
recordId = server.newRecord(title,distance,time,upositive, unegative, bpm,calories,date,comments)

#finalmente hacemos un print con el recordId que nos ha devuelto el webservice.
print recordId
