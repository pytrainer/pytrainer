#!/usr/bin/env python
from optparse import OptionParser
import os, stat
import sys
import logging
import gtk

import httplib, httplib2
import urllib2
import mimetools, mimetypes

class openstreetmap:
	def __init__(self, parent = None, pytrainer_main = None, conf_dir = None, options = None):
		self.parent = parent
		self.pytrainer_main = pytrainer_main
		self.options = options
		self.conf_dir = conf_dir
		self.description = " "
		self.tags = ""
		self.visibility = "private"

	def run(self, id, activity=None):  #TODO Convert to use activity...
		logging.debug(">>")
		uri = "http://api.openstreetmap.org/api/0.6/gpx/create" #URI for uploading traces to OSM
		if 'username' not in self.options or self.options['username'] == "" or 'password' not in self.options or self.options['password'] == "":
			logging.error("Must have username and password configured")
			msg = _("Must have username and password configured")
			md = gtk.MessageDialog(self.pytrainer_main.windowmain.window1, gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_ERROR, gtk.BUTTONS_CLOSE, msg)
			md.set_title(_("Openstreetmap Extension Error"))
			md.run()
			md.destroy()
			return
		username = self.options['username']
		password = self.options['password']
		gpx_file = "%s/gpx/%s.gpx" % (self.conf_dir, id)
		if os.path.isfile(gpx_file):
			#GPX file is ok and found, so open it
			logging.debug("GPX file: %s found, size: %d" % (gpx_file, os.path.getsize(gpx_file)))
			f = open(gpx_file, 'r')
			file_contents = f.read()
			if file_contents.find("<?xml version='1.0' encoding='ASCII'?>") != -1:
				logging.debug("GPX file: %s has ASCII encoding - updating to UTF-8 for OSM support" % gpx_file)
				f.close() 					#Close readonly file
				f = open(gpx_file, 'w') 	#and open file for writing
				file_contents = file_contents.replace("<?xml version='1.0' encoding='ASCII'?>","<?xml version='1.0' encoding='UTF-8'?>", 1)
				f.write(file_contents) 		#Write new content
				f.close() 					#Close
				f = open(gpx_file, 'r') 	#Reopen in readonly mode
			#Get extra info from user
			self.display_options_window()
			fields = (("description",self.description), ("tags",self.tags), ("visibility",self.visibility))
			logging.debug("Added fields: %s" % str(fields))
			#Multipart encode the request
			boundary, body = self.multipart_encode(fields=fields, files=(("file", f),))
			content_type = 'multipart/form-data; boundary=%s' % boundary
			#Finished with the file so close it
			f.close()
			#Add the http headers to the request
			h = httplib2.Http()
			headers = {
				'Content-Type': content_type
			}
			#Add basic authentication credentials to the request
			h.add_credentials(username, password)
			#Show user something is happening
			msg = _("Posting GPX trace to Openstreetmap\n\nPlease wait this could take several minutes")
			md = gtk.MessageDialog(self.pytrainer_main.windowmain.window1, gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_INFO, gtk.BUTTONS_NONE, msg)
			md.set_title(_("Openstreetmap Extension Processing"))
			md.set_modal(True)
			md.show()
			while gtk.events_pending():	# This allows the GUI to update
				gtk.main_iteration()	# before completion of this entire action
			logging.debug("before request posting")
			#POST request to OSM
			res, content = h.request(uri, 'POST', body=body, headers=headers)
			logging.debug("after request posting")
			logging.debug("Got response status: %s, reason: %s, content: %s" % (res.status, res.reason, content))
			if res.reason == 'OK':
				res_msg = "Successfully posted to OSM.\nYou should get an email with the outcome of the upload soon\n\nTrace id is %s" % content
			else:
				res_msg = "Some error occured\nGot a status %s, reason %s\nContent was: %s" % (res.status, res.reason, content)
			#Close 'Please wait' dialog
			md.destroy()
			#Show the user the result
			md = gtk.MessageDialog(self.pytrainer_main.windowmain.window1, gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_INFO, gtk.BUTTONS_OK, res_msg)
			md.set_title(_("Openstreetmap Extension Upload Complete"))
			md.set_modal(False)
			md.run()
			md.destroy()

		else:
			logging.error("GPX file: %s NOT found!!!" % (gpx_file))
		logging.debug("<<")

	def display_options_window(self):
		self.prefwindow = gtk.Dialog(title=_("Please add any additional information for this upload"), parent=None, flags=gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT, buttons=(gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))
		self.prefwindow.set_modal(False)
		table = gtk.Table(1,2)
		self.entryList = []
		#Add description
		label = gtk.Label("<b>Description</b>")
		label.set_use_markup(True)
		entry = gtk.Entry()
		self.entryList.append(entry)
		table.attach(label,0,1,0,1)
		table.attach(entry,1,2,0,1)
		#Add tags
		label = gtk.Label("<b>Tags</b>")
		label.set_use_markup(True)
		entry = gtk.Entry()
		self.entryList.append(entry)
		table.attach(label,0,1,1,2)
		table.attach(entry,1,2,1,2)
		#Add visibility
		label = gtk.Label("<b>Visibility</b>")
		label.set_use_markup(True)
		combobox = gtk.combo_box_new_text()
		combobox.append_text("private")
		combobox.append_text("public")
		combobox.append_text("trackable")
		combobox.append_text("identifiable")
		combobox.set_active(0)
		table.attach(combobox,1,2,2,3)
		self.entryList.append(combobox)
		table.attach(label,0,1,2,3)
		#Buld dialog and show
		self.prefwindow.vbox.pack_start(table)
		self.prefwindow.show_all()
		self.prefwindow.connect("response", self.on_options_ok_clicked)
		self.prefwindow.run()

	def on_options_ok_clicked(self, widget, response_id):
		widget.destroy()
		self.description = self.entryList[0].get_text()
		if self.description == "":
			logging.debug("A description is required - setting to default")
			self.description = "Uploaded from pytrainer"
		self.tags = self.entryList[1].get_text()
		self.visibility = self.entryList[2].get_active_text()
		logging.debug("Description: %s, tags: %s, visibility: %s" % ( self.description, self.tags, self.visibility) )

	def multipart_encode(self, fields, files, boundary = None, buffer = None):
		'''
			Multipart encode data for posting
			 from examples at from http://odin.himinbi.org/MultipartPostHandler.py & http://bitworking.org/projects/httplib2/doc/html/libhttplib2.html
		'''
		if boundary is None:
			boundary = mimetools.choose_boundary()
		if buffer is None:
			buffer = ''
		for (key, value) in fields:
			buffer += '--%s\r\n' % boundary
			buffer += 'Content-Disposition: form-data; name="%s"' % key
			buffer += '\r\n\r\n' + value + '\r\n'
		print files
		for (key, fd) in files:
			file_size = os.fstat(fd.fileno())[stat.ST_SIZE]
			filename = os.path.basename(fd.name)
			contenttype = mimetypes.guess_type(filename)[0] or 'application/octet-stream'
			buffer += '--%s\r\n' % boundary
			buffer += 'Content-Disposition: form-data; name="%s"; filename="%s"\r\n' % (key, filename)
			buffer += 'Content-Type: %s\r\n' % contenttype
			# buffer += 'Content-Length: %s\r\n' % file_size
			fd.seek(0)
			buffer += '\r\n' + fd.read() + '\r\n'
		buffer += '--%s--\r\n\r\n' % boundary
		return boundary, buffer
