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

import logging

class fileUtils:
    def __init__(self, filename, data):
        self.filename = filename
        self.data = data

    def run(self):
        logging.debug('>>')
        if self.data is not None:
            logging.debug("Writing in %s " % self.filename) 
            out = open(self.filename, 'w')
            out.write(self.data)
            out.close()
        else:
            logging.error("Nothing to write in %s" % self.filename)
        logging.debug('<<')


