#!/usr/bin/python
# -*- coding: iso-8859-1 -*-

#Copyright (C) Miguel Angel Otero <maoterodapena@gmail.com>

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

import sys
import os, shutil
import xml.dom.minidom 

from pytrainer.lib.system import checkConf

#Pequeña función para pasar a texto un nodelist del XML
def toString(nodelist):
    s = ""
    for node in nodelist:
        if node.nodeType == node.TEXT_NODE or node.nodeType == node.CDATA_SECTION_NODE:
            s = s + node.data
    return s


#Cogemos las variables de conf.xml
parser = OptionParser()
parser.add_option("-n", "--nikeid", dest="nikeid")
parser.add_option("-m", "--mountpoint", dest="mountpoint")
(options,args) =  parser.parse_args()
nikeid = options.nikeid
mountpoint = options.mountpoint

#Path a los directorios del dispositivo nike
empedsdir="iPod_Control/Device/Trainer/Workouts/Empeds"

#Comprobamos que el iPod está montado
if not os.path.exists(mountpoint):
	f = os.popen("zenity --error --text='No iPod found. Check mountpoint in the configuration.'");
	print 0
	sys.exit()

#Obtenemos el dir donde estan los ficheros del ipod
ipoddir = os.path.join(str(mountpoint),empedsdir+"/"+str(nikeid))

#Comprobación de que el nikeid is correcto
if not os.path.exists(ipoddir):
	msg = ""
	#Si el nikeid no existe, mostramos un mensaje con los nikeid encontrados
	ipoddir=os.path.join(str(mountpoint),empedsdir)
	for f in os.listdir(ipoddir):
		if os.path.isdir(os.path.join(ipoddir,f)):
			msg = msg + f + ", "
	f = os.popen("zenity --error --text='Incorrect nikeid. Try %s or look into %s'" % (msg, empedsdir));
	print 0
	sys.exit()

#Sacamos el dir de los plugins
conf=checkConf()
plugindir=conf.plugindir + "/ipod/"

ipodfiles = []

# Recorro el directorio synched (archivos subidos a nikeplus.com)
# Aqui tambien usamos os.path.join
syncheddir = os.path.join(ipoddir,"synched")
for f in os.listdir(syncheddir):
	files = (f,"/synched")
	# Lo añadimos a la lista sólo si no está copiado en plugindir
	if not os.path.isfile(os.path.join(plugindir,f)):
		ipodfiles.append(files)

# Recorro el directorio latest (archivos no subidos a nikeplus.com)
# Aqui tambien usamos os.path.join
latestdir = os.path.join(ipoddir,"latest")
for f in os.listdir(latestdir):
	# Lo añadimos a la lista sólo si no está copiado
	if not os.path.isfile(os.path.join(plugindir,f)):
		files = (f,"/latest")
		ipodfiles.append(files)

#Mostramos el dialogo con la lista de XMLs disponibles:
ifiles = ""
for i in ipodfiles:
	ifiles = ifiles + " false '"+i[0]+"'"

#Si no hay ninguno, mostramos un mensaje de error
if len(ifiles) == 0:
	f = os.popen("zenity --error --text='There is no new workouts!'");
	print 0
	sys.exit()
	
#Mostramos la lista de ficheros disponibles y recogemos la opcion seleccionada
selected_file = os.popen("zenity --list --text='Select a record' --column='' --radiolist --column='record' %s" % ifiles).read()

#si la opcion es nula, es que no ha seleccionado nada. Imprimimos False y paramos el programa
if selected_file == "":
	print 0 
	sys.exit()

#Si el programa llega hasta aqui es que hemos seleccionado un fichero para importar

#Eliminamos un salto de linea final que devuelve siempre el zenity
selected_file = selected_file.replace("\n","")

#Cogemos el path del fichero seleccionado:
for i in ipodfiles:
	if i[0] == selected_file:
		path_selected_file = ipoddir+"/"+i[1]+"/"+i[0]
		break

#Copiamos el fichero seleccionado al plugindir (home/user/.pytrainer/plugins/ipod).
#igual podemos usar los ficheros en el plugindir para testear despues que tenemos sincronizado. 
shutil.copy(path_selected_file,os.path.join(plugindir,i[0]))

#Sacamos los datos del fichero xml y rellenamos las variables
#ipodxml = xml.dom.minidom.parse(os.path.join(ipoddir, f))
ipodxml = xml.dom.minidom.parse(path_selected_file)
title=toString(ipodxml.getElementsByTagName("workoutName")[0].childNodes)
distance=toString(ipodxml.getElementsByTagName("distance")[0].childNodes)  # distancia en Km
distance_unit=ipodxml.getElementsByTagName("distance")[0].attributes['unit'].value
if distance_unit!='km':
	distance = str (float(distance) * 1.609344)
time=str(int(toString(ipodxml.getElementsByTagName("duration")[0].childNodes))/1000) #Tiempo en segundos
upositive=None #Nivel acumulado positivo, dejalo en nada
unegative=None #Nivel acumulado negativo, dejalo en nada
bpm=None #Es la media de pulsaciones.. como no tienes pulsometro, dejalo en nada
calories=toString(ipodxml.getElementsByTagName("calories")[0].childNodes) #numero de calorias
date=toString(ipodxml.getElementsByTagName("time")[0].childNodes) #fecha en formato ingles
date=date[0:10]
comments=""

#ahora metemos los datos a traves del webservice y recogemos la variable que nos pasa el server.
#En este momento los datos ya son metidos en la base de datos (ojito!!)
import SOAPpy
server = SOAPpy.SOAPProxy("http://localhost:8081/")
recordId = server.newRecord(title,distance,time,upositive, unegative, bpm,calories,date,comments)

#finalmente hacemos un print con el recordId que nos ha devuelto el webservice.
#COn este id la interfaz de pytrainer sabe que dialogo con que datos mostrar
print recordId

