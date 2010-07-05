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
from lib.activity import Activity

class ActivityPool:
	'''
	Class maintains a pool of activities
		size is set at initialisation
	'''
	def __init__(self, pytrainer_main = None, size = 1):
		logging.debug(">>")
		#It is an error to try to initialise with no reference to pytrainer_main
		if pytrainer_main is None:
			print("Error - must initialise with a reference to the main pytrainer class")
			return
		self.pytrainer_main = pytrainer_main
		self.max_size = size
		self.pool = {}
		self.pool_queue = []
		logging.debug("Initialising ActivityPool to size: %d" % size)
		logging.debug("<<")

	def clear_pool(self):
		logging.debug(">>")
		logging.debug("Clearing ActivityPool")
		self.pool = {}
		self.pool_queue = []
		logging.debug("<<")

	def get_activity(self, id):
		sid = str(id)
		if sid in self.pool.keys():
			logging.debug("Found activity in pool")
			#Have accessed this activity, place at end of queue
			self.pool_queue.remove(sid)
			self.pool_queue.append(sid)
		else:
			logging.debug("Activity NOT found in pool")
			self.pool[sid] = Activity(pytrainer_main = self.pytrainer_main, id = id)
			self.pool_queue.append(sid)
		if len(self.pool_queue) > self.max_size:
			sid_to_remove = self.pool_queue.pop(0)
			logging.debug("Removing activity: %s" % sid_to_remove)
			del self.pool[sid_to_remove]
		logging.debug("ActivityPool queue length: %d" % len(self.pool_queue))
		logging.debug("ActivityPool queue: %s" % str(self.pool_queue))
		return self.pool[sid]
