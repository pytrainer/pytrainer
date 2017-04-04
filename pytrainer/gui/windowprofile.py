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

from __future__ import division
from SimpleGladeApp import SimpleGladeApp
from windowcalendar import WindowCalendar
from pytrainer.core.equipment import EquipmentService
from pytrainer.gui.equipment import EquipmentUi
from pytrainer.core.sport import Sport
import gtk
import gobject
import logging
import pytrainer
import pytrainer.util.color
from pytrainer.gui.color import ColorConverter

class WindowProfile(SimpleGladeApp):
    def __init__(self, sport_service, data_path = None, parent=None, pytrainer_main=None):
        glade_path="glade/profile.glade"
        root = "newprofile"
        domain = None
        self.parent = parent
        self.pytrainer_main = pytrainer_main
        self.data_path = data_path
        SimpleGladeApp.__init__(self, data_path+glade_path, root, domain)
        self.conf_options = parent.profile_options
        self.stored_color = pytrainer.util.color.Color(0)
        self._sport_service = sport_service

    def new(self):
        logging.debug(">>")
        self.gender_options = {
            0:_("Male"),
            1:_("Female")
            }

        self.ddbb_type = {
            0:"sqlite",
            1:"mysql"
            }
    
        #anhadimos las opciones al combobox gender
        for i in self.gender_options:
            self.prf_gender.insert_text(i,self.gender_options[i])
        
        #hacemos lo propio para el combobox ddbb 
        for i in self.ddbb_type:
            self.prf_ddbb.insert_text(i,self.ddbb_type[i])

        #preparamos la lista sports:
        column_names=[_("Sport"),_("MET"),_("Extra Weight"), _("Maximum Pace"), _("Color")]
        for column_index, column_name in enumerate(column_names):
            if column_index==4:
                renderer = gtk.CellRendererPixbuf()
            else:
                renderer = gtk.CellRendererText()
            column = gtk.TreeViewColumn(column_name, text=column_index)
            column.pack_start(renderer, expand=False)
            if column_index==4:
                column.add_attribute(renderer, 'pixbuf', column_index)
            else:
                column.add_attribute(renderer, 'text', column_index)
            column.set_resizable(True)
            self.sportTreeView.append_column(column)

        #initialise equipment tab:
        equipment_service = EquipmentService(self.pytrainer_main.ddbb)
        equipment_ui = EquipmentUi(self.data_path + "/glade", equipment_service)
        self.equipment_container.add(equipment_ui) 
        logging.debug("<<")           
        
    def present(self):
        self.newprofile.present()
        
    def setValues(self, list_options):
        logging.debug(">>")
        # Need to think if it does make sense to use pprint -> compatibility issues
        #print list_options
        for i in self.conf_options.keys():
            if not list_options.has_key(i):
                logging.info('No list options for %s' %s)
                continue
            if i == "default_viewer":
                if list_options[i] == "1":
                    logging.info("Setting default map viewer to OSM")
                    self.radiobuttonDefaultOSM.set_active(1)
                else:
                    logging.info("Setting default map viewer to Google")
                    self.radiobuttonDefaultGMap.set_active(1)
            elif i == "prf_startscreen":
                if list_options[i] == "current_day":
                    self.radioButtonStartScreenCurrentDay.set_active(1)
                else:
                    self.radioButtonStartScreenLastEntry.set_active(1)
                logging.info("Setting start screen to display %s" % list_options[i])
            else:
                try:
                    var = getattr(self,i)
                except AttributeError as e:
                    continue                
                if i == "prf_hrzones_karvonen" or i == "prf_us_system":
                    if list_options[i] == "True":
                        logging.info("Setting %s to true" %i)
                        var.set_active(True)
                elif i == "prf_gender":
                    for j in self.gender_options:
                        if self.gender_options[j] == list_options[i]:
                            logging.info("Setting gender to %s" % self.gender_options[j])
                            var.set_active(j)
                elif i == "prf_ddbb":
                    for j in self.ddbb_type:
                        if self.ddbb_type[j] == list_options[i]:
                            logging.info("Setting %s as database engine" % self.ddbb_type[j])
                            var.set_active(j)
                            if j==0:
                                self._ddbb_value_deactive()
                            else:
                                self._ddbb_value_active()
                else:
                    logging.info("Setting %s to %s" % (i,list_options[i]))
                    var.set_text(list_options[i])
        logging.debug("<<")
    
    def saveOptions(self):
        logging.debug(">>")
        list_options = {}
        print self.conf_options
        for i in self.conf_options.keys():
            if i == "default_viewer":
                if self.radiobuttonDefaultOSM.get_active():
                    list_options[i] = "1"
                else:
                    list_options[i] = "0"
            elif i == "prf_startscreen":
                ss_selected = "current_day"
                if self.radioButtonStartScreenLastEntry.get_active():
                    ss_selected = "last_entry"
                list_options[i] = ss_selected
            else:
                try:
                    var = getattr(self,i)
                except AttributeError as e:
                    continue
                if i == "prf_hrzones_karvonen" or i == "prf_us_system":
                    if var.get_active():
                        list_options[i] = "True"
                    else:
                        list_options[i] = "False"
                elif i == "prf_gender" or i == "prf_ddbb":
                    list_options[i] = var.get_active_text()
                else:
                    list_options[i] = var.get_text()
            logging.info("Saving %s as %s" % (i, list_options[i]))
        logging.info("Updating profile...")
        self.parent.setProfile(list_options)
        self.parent.saveProfile()
        logging.debug("<<")
    
    def on_calendar_clicked(self,widget):
        calendardialog = WindowCalendar(self.data_path,self)
        calendardialog.run()

    def setDate(self,date):
        self.prf_age.set_text(date)

    def on_switch_page(self,widget,pointer,frame):
        #print widget, pointer, frame
        if frame==2:
            self.saveOptions()
            sport_list = self._sport_service.get_all_sports()
            store = gtk.ListStore(
                        gobject.TYPE_STRING,
                        gobject.TYPE_STRING,
                        gobject.TYPE_STRING,
                        gobject.TYPE_STRING,
                        gtk.gdk.Pixbuf,
                        object)
            for sport in sport_list:
                iter = store.append()
                colorPixBuf = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB, False, 8, 25, 15)
                colorPixBuf.fill(sport.color.rgba_val)
                store.set(iter,
                    0, sport.name,
                    1, sport.met,
                    2, sport.weight,
                    3, sport.max_pace,
                    4, colorPixBuf)
            self.sportTreeView.set_model(store)
            self.sportTreeView.set_cursor(0)
            self.sportlist.show()
        elif frame == 5: #Startup Parameters page selected
            self.init_params_tab()
    
    def init_params_tab(self):
        #Show log level
        if self.pytrainer_main.startup_options.log_level == logging.ERROR:
            self.comboboxLogLevel.set_active(0)
        elif self.pytrainer_main.startup_options.log_level == logging.WARNING:
            self.comboboxLogLevel.set_active(1)
        elif self.pytrainer_main.startup_options.log_level == logging.INFO:
            self.comboboxLogLevel.set_active(2)
        elif self.pytrainer_main.startup_options.log_level == logging.DEBUG:
            self.comboboxLogLevel.set_active(3)
        else:
            self.comboboxLogLevel.set_active(0)
            print "Unknown logging level specified"

        #Show if validation requested
        if self.pytrainer_main.startup_options.validate:
            self.checkbuttonValidate.set_active(True)
        else:
            self.checkbuttonValidate.set_active(False)
            
        #Show if new graph activated
        if self.pytrainer_main.startup_options.newgraph:
            self.checkbuttonNewGraph.set_active(True)
        else:
            self.checkbuttonNewGraph.set_active(False)
        
    def on_comboboxLogLevel_changed(self, widget):
        active = self.comboboxLogLevel.get_active()
        if active == 1:
            logging.debug("Setting log level to WARNING")
            self.pytrainer_main.startup_options.log_level = logging.WARNING
        elif active == 2:
            logging.debug("Setting log level to INFO")
            self.pytrainer_main.startup_options.log_level = logging.INFO
        elif active == 3:
            logging.debug("Setting log level to DEBUG")
            self.pytrainer_main.startup_options.log_level = logging.DEBUG
        else:
            logging.debug("Setting log level to ERROR")
            self.pytrainer_main.startup_options.log_level = logging.ERROR
        self.pytrainer_main.set_logging_level(self.pytrainer_main.startup_options.log_level)    
        
    def on_checkbuttonValidate_toggled(self, widget):
        if self.checkbuttonValidate.get_active():
            logging.debug( "Validate activated")
            self.pytrainer_main.startup_options.validate = True
        else:
            logging.debug("Validate deactivated")
            self.pytrainer_main.startup_options.validate = False
            
    def on_checkbuttonNewGraph_toggled(self, widget):
        if self.checkbuttonNewGraph.get_active():
            logging.debug("NewGraph activated")
            self.pytrainer_main.startup_options.newgraph = True
        else:
            logging.debug("NewGraph deactivated")
            self.pytrainer_main.startup_options.newgraph = False       
    
    def on_accept_clicked(self,widget):
        self.saveOptions()
        self.close_window()
    
    def on_cancel_clicked(self,widget):
        self.close_window()

    def close_window(self):
        self.newprofile.hide()
        self.newprofile = None
        self.quit()

    def _ddbb_value_active(self):
        self.prf_ddbbhost_label.set_sensitive(1)
        self.prf_ddbbname_label.set_sensitive(1)
        self.prf_ddbbuser_label.set_sensitive(1)
        self.prf_ddbbpass_label.set_sensitive(1)
        self.prf_ddbbhost.set_sensitive(1)
        self.prf_ddbbname.set_sensitive(1)
        self.prf_ddbbuser.set_sensitive(1)
        self.prf_ddbbpass.set_sensitive(1)
    
    def _ddbb_value_deactive(self):
        self.prf_ddbbhost_label.set_sensitive(0)
        self.prf_ddbbname_label.set_sensitive(0)
        self.prf_ddbbuser_label.set_sensitive(0)
        self.prf_ddbbpass_label.set_sensitive(0)
        self.prf_ddbbhost.set_sensitive(0)
        self.prf_ddbbname.set_sensitive(0)
        self.prf_ddbbuser.set_sensitive(0)
        self.prf_ddbbpass.set_sensitive(0)

    def on_prf_ddbb_changed(self,widget):
        i = self.prf_ddbb.get_active_text()
        if i == "mysql":
            self._ddbb_value_active()
        else:
            self._ddbb_value_deactive()

    def on_addsport_clicked(self,widget):
        self.hidesportsteps()
        self.buttonbox.set_sensitive(0)
        self.addsport.show()

    def on_newsport_accept_clicked(self,widget):
        sport = Sport()
        sport.name = unicode(self.newsportentry.get_text())
        sport.met = self._trim_to_null(self.newmetentry.get_text())
        sport.weight = self.newweightentry.get_text()
        sport.max_pace = self._trim_to_null(self.newmaxpace.get_text())
        sport.color = self.stored_color
        if sport.name.lower() in [s.name.lower() for s in self._sport_service.get_all_sports()]:
            msg = "Sport '%s' already exists" % sport.name
            logging.error(msg)
            md = gtk.MessageDialog(None, gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_ERROR, gtk.BUTTONS_CLOSE, _(msg))
            md.set_title(_("Sport Creation Error"))
            md.run()
            md.destroy()
            return
        self._sport_service.store_sport(sport)
        self.pytrainer_main.refreshMainSportList()
        self.on_switch_page(None,None,2)
        self.hidesportsteps()
        self.buttonbox.set_sensitive(1)
        self.sportlist.show()

    def on_delsport_clicked(self,widget):
        selected,iter = self.sportTreeView.get_selection().get_selected()
        if iter:
            self.buttonbox.set_sensitive(0)
            sport = selected.get_value(iter,0)
            self.sportnamedel.set_text(sport)
            self.hidesportsteps()
            self.deletesport.show()

    def on_deletesport_clicked(self,widget):
        sport_name = self.sportnamedel.get_text()
        sport = self._sport_service.get_sport_by_name(sport_name)
        self._sport_service.remove_sport(sport)
        self.pytrainer_main.refreshMainSportList()
        self.on_switch_page(None,None,2)
        self.hidesportsteps()
        self.buttonbox.set_sensitive(1)
        self.sportlist.show()
    
    def on_editsport_clicked(self,widget):
        selected,iter = self.sportTreeView.get_selection().get_selected()
        if iter:
            self.buttonbox.set_sensitive(0)
            sport_desc = selected.get_value(iter,0)
            sport = self._sport_service.get_sport_by_name(sport_desc)
            self.editsportentry.set_text(sport.name)
            self.sportnameedit.set_text(sport.name)
            self.editweightentry.set_text(str(sport.weight))
            met_str = "" if sport.met is None else str(sport.met)
            self.editmetentry.set_text(met_str)
            max_pace_str = "" if sport.max_pace is None else str(sport.max_pace)
            self.editmaxpace.set_text(max_pace_str)
            colorPixBuf = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB, False, 8, 250, 20)
            colorPixBuf.fill(sport.color.rgba_val)
            self.editcolor.set_from_pixbuf(colorPixBuf)
            self.hidesportsteps()
            self.editsport.show()
            
    def on_editcolor_clicked(self, widget):
        selected,iter = self.sportTreeView.get_selection().get_selected()
        if iter:
            sport_desc = selected.get_value(iter,0)
            sport = self._sport_service.get_sport_by_name(sport_desc)
            colorseldlg = gtk.ColorSelectionDialog("test")
            colorseldlg.colorsel.set_has_palette(True)
            colorseldlg.colorsel.set_current_color(ColorConverter().convert_to_gdk_color(sport.color))
            colorseldlg.run()
            gdk_color = colorseldlg.colorsel.get_current_color()
            self.stored_color = ColorConverter().convert_to_color(gdk_color)
            colorPixBuf = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB, False, 8, 250, 20)
            colorPixBuf.fill(self.stored_color.rgba_val)
            self.newcolor.set_from_pixbuf(colorPixBuf)
            self.editcolor.set_from_pixbuf(colorPixBuf)
            
            colorseldlg.hide()
            
    def on_sporttreeview_row_activated(self, widget, path, column):
        self.on_editsport_clicked(None)
    
    def on_editsport_accept_clicked(self,widget):
        oldnamesport = self.sportnameedit.get_text()
        sport = self._sport_service.get_sport_by_name(oldnamesport)
        sport.name = unicode(self.editsportentry.get_text())
        sport.weight = self.editweightentry.get_text()
        sport.met = self._trim_to_null(self.editmetentry.get_text())
        sport.max_pace = self._trim_to_null(self.editmaxpace.get_text())
        sport.color = self.stored_color
        self._sport_service.store_sport(sport)
        self.pytrainer_main.refreshMainSportList()
        self.on_switch_page(None,None,2)
        self.hidesportsteps()
        self.buttonbox.set_sensitive(1)
        self.sportlist.show()
        
    def _trim_to_null(self, string):
        trimmed = string.strip()
        return None if trimmed == "" else trimmed
        
    def on_sportcancel_clicked(self,widget):
        self.hidesportsteps()
        self.buttonbox.set_sensitive(1)
        self.sportlist.show()

    def on_calculatemaxhr_clicked(self,widget=None):
        import datetime
        today = "%s"%datetime.date.today()
        year1,month1,day1 = today.split("-")
        year2,month2,day2 = self.prf_age.get_text().split("-")
        diff = datetime.datetime(int(year1), int(month1), int(day1),0,0,0) - datetime.datetime(int(year2), int(month2), int(day2),0,0,0)
        self.prf_maxhr.set_text("%d" %(220-int(diff.days/365)))

    def hidesportsteps(self):
        self.sportlist.hide()
        self.addsport.hide()
        self.deletesport.hide()
        self.editsport.hide()   
