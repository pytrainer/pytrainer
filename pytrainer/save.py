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

from .lib.fileUtils import fileUtils
from pytrainer.gui.dialogs import save_file_chooser_dialog
import logging
import traceback

class Save:
    def __init__(self, data_path = None, record = None):
        self.record = record
        self.data_path = data_path

    def run(self):
        logging.debug('>>')
        filename = save_file_chooser_dialog(title="savecsvfile", pattern="*.csv")
        records = self.record.getAllrecord()
        # CSV Header
        content = "date_time_local,title,sports.name,distance,duration,average,maxspeed,pace,maxpace,beats,maxbeats,calories,upositive,unegative,comments\n"
        try:
            for record in records:
                line = ""
                for i, data in enumerate(record):
                    if i in [3, 5, 6, 7, 8, 12, 13]:
                        try:
                            data = round(data, 2)
                        except:
                            pass             
                    data = "%s" %data
                    data = data.replace(",", " ")  
                    data = data.replace("\n", " ")             
                    data = data.replace("\r", " ")          
                    if i>0: 
                        line += ",%s" %data
                    else:
                        line += "%s" %data      
                content += "%s\n" %line
            logging.info("Record data successfully retrieved. Choosing file to save it")
            file = fileUtils(filename,content)
            file.run()
        except:
            logging.debug("Traceback: %s" % traceback.format_exc())
        logging.debug('<<')

