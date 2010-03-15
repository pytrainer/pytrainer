#!/usr/bin/env python
from optparse import OptionParser
import os
import sys

class openstreetmap:
	def __init__(self, parent = None, pytrainer_main = None, conf_dir = None, options = None):
		#TODO could use some logging
		self.parent = parent
		self.pytrainer_main = pytrainer_main
		self.options = options
		self.conf_dir = conf_dir

	def run(self, id):
		options = self.options
		print options
		print "Record id: %s" % str(id)
		print "THIS DOESNT WORK YET!!!!"
