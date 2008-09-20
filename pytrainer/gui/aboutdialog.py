# -*- coding: iso-8859-1 -*-

#Copyright (C) Fiz Vazquez vud1@sindominio.net
# Jakinbidea & Grupo Ikusnet Developer
# vud1@grupoikusnet.com
# Heavily modified by dgranda

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

import gtk

class About:
	def __init__(self,data_path = None, version = None):
		self.data_path = data_path
		self.version = version

	def run(self):
		authors = ["Fiz Vázquez <vud1@sindominio.net>\nDavid García Granda <dgranda@gmail.com>"]
		translator_credits = "Basque: Jabier Santamaria <mendikote@gmail.com>\nCatalan: Eloi Crespillo Itchart <eloi@ikuszen.com>\nCzech: Lobus Pokorny <sp.pok@seznam.cz>\nFrench: Dj <dj@djremixtheblog.be>\nFrench: Pierre Gaigé <pgaige@free.fr>\nNorwegian: Havard Davidsen <havard.davidsen@gmail.com>\nPolish: Seweryn Kokot <skokot@po.opole.pl>\nGerman: Aleks <aleks@schnecklecker.de>\nSpanish: Fiz Vázquez <vud1@sindominio.net>"
		about_dialog = gtk.AboutDialog()
		about_dialog.set_destroy_with_parent(True)
		about_dialog.set_name("pyTrainer")
		about_dialog.set_version(self.version)
		about_dialog.set_copyright("Copyright \xc2\xa9 2005-8 Fiz Vázquez")
		about_dialog.set_website("http://sourceforge.net/projects/pytrainer")
		about_dialog.set_comments("Track sporting activities and performance")
		about_dialog.set_license("GNU GPL v2 or later\nPlease check http://www.gnu.org/licenses/old-licenses/gpl-2.0.html")
		about_dialog.set_authors(authors)
		about_dialog.set_translator_credits(translator_credits)
		about_dialog.set_logo(gtk.gdk.pixbuf_new_from_file(self.data_path+"glade/pytrainer_mini.png"))

		# callbacks for destroying the dialog
		def close(dialog, response, editor):
			editor.about_dialog = None
			dialog.destroy()
		def delete_event(dialog, event, editor):
			editor.about_dialog = None
			return True
		
		about_dialog.connect("response", close, self)
		about_dialog.connect("delete-event", delete_event, self)  
		self.about_dialog = about_dialog
		about_dialog.show()
		
