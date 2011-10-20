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
#Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA

import gtk
import pytrainer.lib.webUtils

class About:
    def __init__(self,data_path = None, version = None):
        def url_hook(dialog, url):
            pytrainer.lib.webUtils.open_url_in_browser(url)
        # Available in PyGTK 2.6 and above
        gtk.about_dialog_set_url_hook(url_hook)     
        self.data_path = data_path
        self.version = version

    def run(self):
        authors = ["Fiz Vázquez <vud1@sindominio.net>\nDavid García Granda <dgranda@gmail.com>\nJohn Blance <john.blance@gmail.com>\nArnd Zapletal <a.zapletal@gmail.com>\nNathan Jones <nathan@ncjones.com>\n\n-Package maintainers:\n\nRedHat/Fedora: Douglas E. Warner <silfreed@silfreed.net>\nDebian: Noèl Köthe <noel@debian.org>\nUbuntu: Kevin Dwyer <kevin@pheared.net>, Alessio Treglia <quadrispro@ubuntu.com>"]
        translator_credits = "Euskara: Jabier Santamaria <mendikote@gmail.com>\nCatalà: Eloi Crespillo Itchart <eloi@ikuszen.com>\nČesky: Lobus Pokorny <sp.pok@seznam.cz>\nFrançais: Dj <dj@djremixtheblog.be>, Pierre Gaigé <pgaige@free.fr>, Christian Perrier <bubulle@debian.org>\nNorsk: Havard Davidsen <havard.davidsen@gmail.com>\nPolski: Seweryn Kokot <skokot@po.opole.pl>\nDeutsch: Aleks <aleks@schnecklecker.de>, Noèl Köthe <noel@debian.org>\nEspañol: Fiz Vázquez <vud1@sindominio.net>, David García Granda <dgranda@gmail.com>\nSvenska: Per Medin <per.medin@gmail.com>\nGalego: Kaptan <khanyux@gmail.com>\nPortuguês: Pedro Ribeiro <p.m42.ribeiro@gmail.com>"
        license = "pytrainer - The free sport tracking center\nCopyright (C) 2005-09 Fiz Vázquez\n\nThis program is free software; you can redistribute it and/or modify\nit under the terms of the GNU General Public License as published by\nthe Free Software Foundation; either version 2 of the License, or\n(at your option) any later version.\n\nThis program is distributed in the hope that it will be useful,\nbut WITHOUT ANY WARRANTY; without even the implied warranty of\nMERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the\nGNU General Public License for more details.\n\nYou should have received a copy of the GNU General Public License\nalong with this program; if not, write to the Free Software\nFoundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA"
        about_dialog = gtk.AboutDialog()
        about_dialog.set_destroy_with_parent(True)
        about_dialog.set_name("pytrainer")
        about_dialog.set_version(self.version)
        about_dialog.set_copyright("Copyright \xc2\xa9 2005-09 Fiz Vázquez")
        about_dialog.set_website("http://sourceforge.net/projects/pytrainer")
        about_dialog.set_website_label("http://sourceforge.net/projects/pytrainer")
        about_dialog.set_comments("The free sport tracking center")
        about_dialog.set_license(license)
        
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
        
    def present(self):
        if self.about_dialog is None:
            self.run()
        self.about_dialog.present()
