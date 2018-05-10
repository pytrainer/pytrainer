#!/usr/bin/python
# -*- coding: utf-8 -*-

#Copyright (C) Fiz Vazquez vud1@sindominio.net
# Modified by dgranda

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

import os
import logging
import matplotlib
from gi.repository import GObject
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GdkPixbuf

import dateutil.parser

from SimpleGladeApp import SimpleBuilderApp
from popupmenu import PopupMenu
from aboutdialog import About

import pytrainer.record
from pytrainer.lib.date import Date, second2time
from pytrainer.lib.xmlUtils import XMLParser
#from pytrainer.lib.gpx import Gpx

from pytrainer.recordgraph import RecordGraph
from pytrainer.weekgraph import WeekGraph
from pytrainer.monthgraph import MonthGraph
from pytrainer.yeargraph import YearGraph
from pytrainer.totalgraph import TotalGraph
from pytrainer.heartrategraph import HeartRateGraph

from pytrainer.gui.drawGraph import DrawGraph
from pytrainer.gui.windowcalendar import WindowCalendar
from pytrainer.lib.listview import ListSearch
from pytrainer.lib.uc import UC
from pytrainer.core.activity import Activity
from pytrainer.lib.localization import gtk_str
from sqlalchemy import and_


class Main(SimpleBuilderApp):
    def __init__(self, sport_service, data_path = None, parent = None, version = None, gpxDir = None):
        self._sport_service = sport_service
        self.version = version
        self.parent = parent
        self.pytrainer_main = parent
        self.data_path = data_path
        self.uc = UC()
        SimpleBuilderApp.__init__(self, "pytrainer.ui")

        self.popup = PopupMenu(data_path,self)

        self.block = False
        self.activeSport = None
        self.gpxDir = gpxDir
        self.record_list = None
        self.laps = None

        #Setup graph
        self.grapher = DrawGraph(self, self.pytrainer_main)

        self.y1_limits = None
        self.y1_color = None
        self.y1_linewidth = 1
        # setup Search ListView
        self.listsearch = ListSearch(sport_service, self, self.pytrainer_main)

        self.aboutwindow = None
        self.mapviewer = None
        self.mapviewer_fs = None
        self.waypointeditor = None

    def new(self):
        self.menublocking = 0
        self.selected_view="day"
        self.window1.set_title ("pytrainer %s" % self.version)
        try:
            width, height = self.pytrainer_main.profile.getValue("pytraining","window_size").split(',')
            self.window1.resize(int(width), int(height))
        except:
            pass
        self.record_list = []
        #create the columns for the listdayrecord
        columns = [{'name':_("id"), 'visible':False},{'name':_("Start"), }, {'name':_("Sport")},{'name':self.uc.unit_distance}]
        self.create_treeview(self.recordTreeView,columns)
        #create the columns for the listarea
        # different codings for mean see eg http://de.wikipedia.org/wiki/%C3%98#Kodierung
        columns=[   {'name':_("id"), 'visible':False},
                    {'name':_("Title")},
                    {'name':_("Date")},
                    {'name':_("Distance"), 'xalign':1.0, 'format_float':'%.2f', 'quantity': 'distance'},
                    {'name':_("Sport")},
                    {'name':_("Time"), 'xalign':1.0, 'format_duration':True},
                    {'name':_(u"\u2300 HR"), 'xalign':1.0},
                    {'name':_(u"\u2300 Speed"), 'xalign':1.0, 'format_float':'%.1f', 'quantity': 'speed'},
                    {'name':_("Calories"), 'xalign':1.0}
                ]
        self.create_treeview(self.allRecordTreeView,columns)
        self.create_menulist(columns)
        #create the columns for the waypoints treeview
        columns=[{'name':_("id"), 'visible':False},{'name':_("Waypoint")}]
        self.create_treeview(self.waypointTreeView,columns)
        #create the columns for the athlete history treeview
        columns=[   {'name':_("id"), 'visible':False},
                    {'name':_("Date")},
                    {'name':_("Weight"), 'xalign':1.0, 'quantity':'weight', 'format_float':'%.1f'},
                    {'name':_("Body Fat %"), 'xalign':1.0},
                    {'name':_("Resting HR"), 'xalign':1.0},
                    {'name':_("Max HR"), 'xalign':1.0}
                ]
        self.create_treeview(self.athleteTreeView,columns)
        #create the columns for the stats treeview
        columns=[   {'name':_("id"), 'visible':False},
                    {'name':_("Sport")},
                    {'name':_("Records"), 'xalign':1.0},
                    {'name':_("Total duration"), 'xalign':1.0, 'format_duration':True},
                    {'name':_("Total distance"), 'xalign':1.0, 'format_float':'%.1f', 'quantity':'distance'},
                    {'name':_("Avg speed"), 'format_float':'%.2f', 'quantity':'maxspeed', 'xalign':1.0},
                    {'name':_("Max speed"), 'format_float':'%.2f', 'quantity':'maxspeed', 'xalign':1.0},
                    {'name':_("Avg HR"), 'xalign':1.0},
                    {'name':_("Max HR"), 'xalign':1.0},
                    {'name':_("Max duration"), 'xalign':1.0, 'format_duration':True},
                    {'name':_("Max distance"), 'xalign':1.0, 'format_float':'%.1f', 'quantity':'distance'},
                ]
        self.create_treeview(self.statsTreeView,columns)

        #create the columns for the laps treeview
        columns=[
                    {'name':_("Lap")},
                    {'name':_("Trigger"), 'xalign':0, 'pixbuf':True},
                    {'name':_("Distance"), 'xalign':1.0, 'format_float':'%.2f', 'quantity':'distance'},
                    {'name':_("Time"), 'xalign':1.0, 'format_duration':True},
                    {'name':_("Avg speed"), 'format_float':'%.2f', 'quantity':'speed'},
                    {'name':_("Max speed"), 'format_float':'%.2f', 'quantity':'speed'},
                    {'name':_("Avg pace"), 'xalign':1.0, 'quantity':'pace'},
                    {'name':_("Max pace"), 'xalign':1.0, 'quantity':'pace'},
                    {'name':_("Avg HR"), 'xalign':1.0},
                    {'name':_("Max HR"), 'xalign':1.0},
                    {'name':_("Calories"), 'xalign':1.0},
                    {'name':_("Intensity"), 'visible':False},
                    {'name':_("Comments"), 'xalign':0.0},
                ]
        self.create_treeview(self.lapsTreeView,columns)

        #create the columns for the projected times treeview
        columns=[
                    {'name':_("id"), 'visible':False},
                    {'name':_("Race"), 'xalign':1.0},
                    {'name':_("Distance"), 'xalign':1.0, 'format_float':'%.2f', 'quantity':'distance'},
                    {'name':_("Time"), 'xalign':1.0, 'format_duration':True},
                ]
        self.create_treeview(self.analyticsTreeView,columns,sortable=False)

        #create the columns for the rank treeview
        columns=[
                    {'name':_("id"), 'visible':False},
                    {'name':_("Rank"), 'visible':True},
                    {'name':_("Date"), 'xalign':1.0},
                    {'name':_("Distance"), 'xalign':1.0, 'format_float':'%.2f', 'quantity':'distance'},
                    {'name':_("Time"), 'xalign':1.0, 'format_duration':True},
                    {'name':_("Speed"),  'format_float':'%.2f', 'quantity':'speed'},
                    {'name':_("Pace"),  'format_float':'%.2f', 'quantity':'pace'},
                    {'name':_("Color"), 'visible':False},
                ]
        self.create_treeview(self.rankingTreeView,columns,sortable=False)

        self.fileconf = self.pytrainer_main.profile.confdir+"/listviewmenu.xml"
        if not os.path.isfile(self.fileconf):
            self._createXmlListView(self.fileconf)
        self.showAllRecordTreeViewColumns()
        self.allRecordTreeView.set_search_column(1)
        self.notebook.set_current_page(1)

        #Set correct map viewer
        if self.pytrainer_main.profile.getValue("pytraining","default_viewer") == "1":
            self.radiobuttonOSM.set_active(1)
        else:
            self.radiobuttonGMap.set_active(1)
        self.comboMapLineType.set_active(0)

    def _float_or(self, value, default):
        '''Function to parse and return a float, or the default if the parsing fails'''
        try:
            result = float(value)
        except Exception as e:
            #print type(e)
            #print e
            result = default
        return result

    def setup(self):
        logging.debug(">>")
        self.createGraphs()
        self.createMap()
        page = self.notebook.get_current_page()
        self.on_page_change(None,None,page)
        logging.debug("<<")

    def _createXmlListView(self,file):
        menufile = XMLParser(file)
        savedOptions = []
        savedOptions.append(("date","True"))
        savedOptions.append(("distance","True"))
        savedOptions.append(("average","False"))
        savedOptions.append(("title","True"))
        savedOptions.append(("sport","True"))
        savedOptions.append(("id_record","False"))
        savedOptions.append(("time","False"))
        savedOptions.append(("beats","False"))
        savedOptions.append(("calories","False"))
        menufile.createXMLFile("listviewmenu",savedOptions)

    def removeImportPlugin(self, plugin):
        for widget in self.menuitem1_menu:
            if widget.get_name() == plugin[1]:
                self.menuitem1_menu.remove(widget)

    def removeExtension(self, extension):
        for widget in self.recordbuttons_hbox:
            if widget.get_name() == extension[1]:
                logging.debug("Removing extension: %s " % extension[0])
                self.recordbuttons_hbox.remove(widget)

    def addImportPlugin(self,plugin):
        button = Gtk.MenuItem(plugin[0])
        button.set_name(plugin[1])
        button.connect("activate", self.parent.runPlugin, plugin[1])
        self.menuitem1_menu.insert(button,3)
        self.menuitem1_menu.show_all()

    def addExtension(self,extension):
        #txtbutton,extensioncode,extensiontype = extension
        button = Gtk.Button(extension[0])
        button.set_name(extension[1])
        button.connect("button_press_event", self.runExtension, extension)
        self.recordbuttons_hbox.pack_start(button,False,False,0)
        self.recordbuttons_hbox.show_all()

    def runExtension(self,widget,widget2,extension):
        #print extension
        txtbutton,extensioncode,extensiontype = extension
        id = None
        if extensiontype=="record":
            selected,iter = self.recordTreeView.get_selection().get_selected()
            id = selected.get_value(iter,0)
        self.parent.runExtension(extension,id)

    def createGraphs(self):
        logging.debug(">>")
        self.drawarearecord = RecordGraph(self.record_graph_vbox, self.window1, self.record_combovalue, self.record_combovalue2, self.btnShowLaps, self.tableConfigY1, pytrainer_main=self.pytrainer_main)
        self.drawareaheartrate = HeartRateGraph(self.heartrate_vbox, self.window1, self.heartrate_vbox2, pytrainer_main=self.pytrainer_main)
        self.day_vbox.hide()
        sports = self._sport_service.get_all_sports()
        self.drawareaweek = WeekGraph(sports, self.weekview, self.window1, self.week_combovalue, self.week_combovalue2, self.pytrainer_main)
        self.drawareamonth = MonthGraph(sports, self.month_vbox, self.window1, self.month_combovalue,self.month_combovalue2, self.pytrainer_main)
        self.drawareayear = YearGraph(sports, self.year_vbox, self.window1, self.year_combovalue,self.year_combovalue2, self.pytrainer_main)
        self.drawareatotal = TotalGraph(sports, self.total_vbox, self.window1, self.total_combovalue,self.total_combovalue2, self.pytrainer_main)
        logging.debug("<<")

    def createMap(self):
        logging.debug(">>")
        if not self.mapviewer and not self.mapviewer_fs and not self.waypointeditor:
            try:
                from pytrainer.extensions.mapviewer import MapViewer
                from pytrainer.extensions.waypointeditor import WaypointEditor
                self.mapviewer = MapViewer(self.data_path, pytrainer_main=self.parent, box=self.map_vbox)
                self.mapviewer_fs = MapViewer(self.data_path, pytrainer_main=self.parent, box=self.map_vbox_old)
                self.waypointeditor = WaypointEditor(self.data_path, self.waypointvbox,
                                                     self.pytrainer_main.waypoint,
                                                     parent=self.pytrainer_main)
            except ImportError:
                logging.error("Webkit not found, map functionality not available")
                for container in self.map_vbox, self.map_vbox_old, self.waypointvbox:
                    message = Gtk.Label(_("Webkit not found, map functionality not available"))
                    message.set_selectable(True)
                    container.foreach(lambda widget:container.remove(widget))
                    container.add(message)
                    container.show_all()
        logging.debug("<<")

    def updateSportList(self,listSport):
        logging.debug(">>")
        liststore =  self.sportlist.get_model()
        firstEntry = _("All Sports")
        liststore.clear() #Delete all items
        #Re-add "All Sports"
        liststore.append([firstEntry])
        #Re-add all sports in listSport
        for sport in listSport:
            liststore.append([sport.name])
        self.sportlist.set_active(0)
        logging.debug("<<")

    def render_duration(self, column, cell, model, iter, notif):
        orig = cell.get_property('text')
        if not ':' in orig:
            h,m,s = second2time(int(orig))
            new = '%d:%02d:%02d' % (h,m,s)
        else:
            new = orig
        if orig[:4] == ' 0:0':
            new = orig[4:]
        elif orig[:3] == ' 0:':
            new = orig[3:]
        if len(new)>5:
            hours = int(new[:-6])
            days = _("d")
            if hours>23:
                new = "%d %s %02d:%s" % (hours / 24, days, hours%24 ,new[-5:])
        cell.set_property('text', new)

    def render_float(self, column, cell, model, iter, data):
        _format, _quantity, _idx = data
        _val = model.get_value(iter, _idx)
        _val = self.uc.sys2usr(_quantity, _val)
        _val_str = _format % float(_val)
        cell.set_property('text', _val_str)

    def create_treeview(self,treeview,columns,sortable=True):
        for column_index, column_dict in enumerate(columns):
            if 'pixbuf' in column_dict:
                renderer = Gtk.CellRendererPixbuf()
            else:
                renderer = Gtk.CellRendererText()
            column = Gtk.TreeViewColumn(column_dict['name'])
            column.pack_start(renderer, False)
            if 'pixbuf' in column_dict:
                column.add_attribute(renderer, 'pixbuf', column_index)
            else:
                column.add_attribute(renderer, 'text', column_index)
            column.set_resizable(True)
            column.set_sizing(Gtk.TreeViewColumnSizing.AUTOSIZE)
            if 'xalign' in column_dict:
                renderer.set_property('xalign', column_dict['xalign'])
            if 'visible' in column_dict:
                column.set_visible(column_dict['visible'])
            if 'format_float' in column_dict:
                column.set_cell_data_func(renderer, self.render_float, [column_dict['format_float'], column_dict['quantity'], column_index])
            if 'format_duration' in column_dict and column_dict['format_duration']:
                column.set_cell_data_func(renderer, self.render_duration)
            if sortable:
                column.set_sort_column_id(column_index)
            treeview.append_column(column)

    def actualize_recordview(self,activity):
        logging.debug(">>")
        if activity.id is None:
            #Blank out fields
            self.record_distance.set_text("")
            self.record_upositive.set_text("")
            self.record_unegative.set_text("")
            self.record_average.set_text("")
            self.record_maxspeed.set_text("")
            self.record_pace.set_text("")
            self.record_maxpace.set_text("")
            self.record_sport.set_text("")
            self.record_date.set_text("")
            self.record_time.set_text("")
            self.record_duration.set_text("")
            #self.record_minute.set_text("")
            #self.record_second.set_text("")
            self.record_calories.set_text("")
            self.record_title.set_text("")
            self.label_record_equipment.set_text("")
            self.frame_laps.hide()
            com_buffer = self.record_comments.get_buffer()
            start,end = com_buffer.get_bounds()
            com_buffer.set_text("")
            #Move to main record page and grey out
            self.recordview.set_current_page(0)
            self.recordview.set_sensitive(0)
            logging.debug("<<")
            return
        #Set the units for the activity results, e.g. km, km/h etc
        self.r_distance_unit.set_text(self.uc.unit_distance)
        self.r_speed_unit.set_text(self.uc.unit_speed)
        self.r_maxspeed_unit.set_text(self.uc.unit_speed)
        self.r_pace_unit.set_text(self.uc.unit_pace)
        self.r_maxpace_unit.set_text(self.uc.unit_pace)
        self.r_ascent_unit.set_text(self.uc.unit_height)
        self.r_descent_unit.set_text(self.uc.unit_height)

        if activity.has_data:
            self.recordview.set_sensitive(1)

            dateTime = activity.date_time
            recordDateTime = dateTime.strftime("%Y-%m-%d %H:%M:%S")
            recordDate = dateTime.strftime("%x")
            recordTime = dateTime.strftime("%X")
            recordDateTimeOffset = dateTime.strftime("%z")

            self.record_distance.set_text(activity.get_value_f('distance', "%0.2f"))
            self.record_upositive.set_text(activity.get_value_f('upositive', "%0.2f"))
            self.record_unegative.set_text(activity.get_value_f('unegative', "%0.2f"))
            self.record_average.set_text(activity.get_value_f('average', "%0.2f"))
            self.record_maxspeed.set_text(activity.get_value_f('maxspeed', "%0.2f"))
            self.record_pace.set_text(activity.get_value_f('pace', "%s"))
            self.record_maxpace.set_text(activity.get_value_f('maxpace', "%s"))

            self.record_sport.set_text(activity.sport_name)
            self.record_date.set_text(recordDate)
            self.record_time.set_text(recordTime)
            self.record_duration.set_text(activity.get_value_f('time', '%s'))
            self.record_calories.set_text(activity.get_value_f('calories', "%0.0f"))
            if activity.title:
                self.record_title.set_text(activity.title)
            else:
                self.record_title.set_text('')
            hrun,mrun,srun = second2time(activity.duration)
            hpause,mpause,spause = second2time(activity.time_pause)
            self.record_runrest.set_text("%02d:%02d:%02d / %02d:%02d:%02d" %(hrun,mrun,srun,hpause,mpause,spause))
            buffer = self.record_comments.get_buffer()
            if activity.comments:
                buffer.set_text(activity.comments)
            else:
                buffer.set_text('')
            if len(activity.equipment) > 0:
                equipment_text = ", ".join(map(lambda(item): item.description, activity.equipment))
                self.label_record_equipment.set_text(equipment_text)
            else:
                self.label_record_equipment.set_markup("<i>None</i>")
            if len(activity.Laps)>1:
                store = Gtk.ListStore(
                    GObject.TYPE_INT,
                    GdkPixbuf.Pixbuf,
                    GObject.TYPE_FLOAT,
                    GObject.TYPE_STRING,
                    GObject.TYPE_FLOAT,
                    GObject.TYPE_FLOAT,
                    GObject.TYPE_STRING,
                    GObject.TYPE_STRING,
                    GObject.TYPE_INT,
                    GObject.TYPE_INT,
                    GObject.TYPE_INT,
                    GObject.TYPE_STRING,
                    GObject.TYPE_STRING,
                    )
                for lap in activity.Laps:
                    t = lap.duration
                    m = lap.distance

                    m = self.uc.speed(m)

                    s = m / float(t) * 3.6
                    max_speed = lap.max_speed * 3.6
                    if s > 0:
                        pace = "%d:%02d" %((3600/s)/60,(3600/s)%60)
                        if max_speed >0:
                            max_pace = "%d:%02d" %((3600/max_speed)/60,(3600/max_speed)%60)
                        else:
                            max_pace = "0:00"
                    else:
                        pace = "0:00"
                        max_pace = "0:00"

                    color = {
                        'active' : '#000000',
                        'rest' : '#808080',
                        'resting' : '#808080',
                    }

                    pic = GdkPixbuf.Pixbuf.new_from_file(self.data_path+"glade/trigger_%s.png" % lap.laptrigger)

                    iter = store.append()
                    store.set(iter,
                        0, lap.lap_number + 1,
                        1, pic,
                        2, m/1000,
                        3, str(int(float(t))),
                        4, s,
                        5, max_speed,
                        6, pace,
                        7, max_pace,
                        8, lap.avg_hr if lap.avg_hr else 0,
                        9, lap.max_hr if lap.max_hr else 0,
                        10, lap.calories,
                        11, color[lap.intensity],
                        12, '' if not lap.comments else (lap.comments if len(lap.comments)<40 else "%s..." % lap.comments[:40]),
                        )
                self.lapsTreeView.set_model(store)
                self.lapsTreeView.set_rules_hint(True)

                # Use grey color for "rest" laps
                for c in self.lapsTreeView.get_columns():
                    for cr in c.get_cells():
                        if type(cr)==Gtk.CellRendererText:
                            cr.set_property('foreground', 'gray')

                def edited_cb(cell, path, new_text, (liststore, activity)):
                    liststore[path][12] = new_text
                    activity.Laps[int(path)].comments = gtk_str(new_text)
                    self.pytrainer_main.ddbb.session.commit()

                def show_tooltip(widget, x, y, keyboard_mode, tooltip, user_param1):
                     path = self.lapsTreeView.get_path_at_pos(x,y-20)
                     if not path: return False
                     if path[1] != self.lapsTreeView.get_columns()[12]: return False
                     comments = user_param1[1].laps[path[0][0]]['comments']
                     if comments and len(comments)>40:
                         tooltip.set_text(comments)
                         return True
                     return False

                if getattr(self.lapsTreeView, 'tooltip_handler_id', None):
                    self.lapsTreeView.disconnect(self.lapsTreeView.tooltip_handler_id)
                self.lapsTreeView.tooltip_handler_id = self.lapsTreeView.connect('query-tooltip', show_tooltip, (store, activity))
                i = 0
                for cr in self.lapsTreeView.get_columns()[12].get_cells():
                    cr.set_property('editable', True)
                    if getattr(self, 'lapview_handler_id', None):
                        cr.disconnect(self.lapview_handler_id)
                    self.lapview_handler_id = cr.connect('edited', edited_cb, (store, activity))
                    tooltip = Gtk.Tooltip()
                    tooltip.set_text(activity.laps[i]['comments'])
                    # FIXME Use TreePath to set tooltip
                    #self.lapsTreeView.set_tooltip_cell(tooltip, i, self.lapsTreeView.get_columns()[12], cr)
                    self.lapsTreeView.set_tooltip_cell(tooltip, None, self.lapsTreeView.get_columns()[12], cr)
                    i += 1
                self.frame_laps.show()
            else:
                self.frame_laps.hide()

        else:
            self.recordview.set_current_page(0)
            self.recordview.set_sensitive(0)

        logging.debug("<<")

    def actualize_recordgraph(self,activity):
        logging.debug(">>")
        self.record_list = activity.tracks
        self.laps = activity.laps
        if activity.gpx_file is not None:
            if not self.pytrainer_main.startup_options.newgraph:
                logging.debug("Using the original graphing")
                logging.debug("Activity has GPX data")
                #Show drop down boxes
                self.hbox30.show()
                #Hide new graph details
                self.graph_data_hbox.hide()
                self.hboxGraphOptions.hide()
                #Enable graph
                self.record_vbox.set_sensitive(1)
                self.drawarearecord.drawgraph(self.record_list,self.laps)
            else:
                #Still just test code....
                logging.debug("Using the new TEST graphing approach")
                #Hide current drop down boxes
                self.hbox30.hide()
                self.graph_data_hbox.hide()
                #Enable graph
                self.record_vbox.set_sensitive(1)
                #Create a frame showing data available for graphing
                #Remove existing frames
                for child in self.graph_data_hbox.get_children():
                    if isinstance(child, Gtk.Frame):
                        self.graph_data_hbox.remove(child)
                #Build frames and vboxs to hold checkbuttons
                xFrame = Gtk.Frame(label=_("Show on X Axis"))
                y1Frame = Gtk.Frame(label=_("Show on Y1 Axis"))
                y2Frame = Gtk.Frame(label=_("Show on Y2 Axis"))
                limitsFrame = Gtk.Frame(label=_("Axis Limits"))
                xvbox = Gtk.VBox()
                y1box = Gtk.Table()
                y2box = Gtk.Table()
                limitsbox = Gtk.Table()
                #Populate X axis data
                #Create x axis items
                xdistancebutton = Gtk.RadioButton(label=_("Distance"))
                xtimebutton = Gtk.RadioButton(group=xdistancebutton, label=_("Time"))
                xlapsbutton = Gtk.CheckButton(label=_("Laps"))
                y1gridbutton = Gtk.CheckButton(label=_("Left Axis Grid"))
                y2gridbutton = Gtk.CheckButton(label=_("Right Axis Grid"))
                xgridbutton = Gtk.CheckButton(label=_("X Axis Grid"))
                #Set state of buttons
                if activity.x_axis == "distance":
                    xdistancebutton.set_active(True)
                elif activity.x_axis == "time":
                    xtimebutton.set_active(True)
                xlapsbutton.set_active(activity.show_laps)
                y1gridbutton.set_active(activity.y1_grid)
                y2gridbutton.set_active(activity.y2_grid)
                xgridbutton.set_active(activity.x_grid)
                #Connect handlers to buttons
                xdistancebutton.connect("toggled", self.on_xaxischange, "distance", activity)
                xtimebutton.connect("toggled", self.on_xaxischange, "time", activity)
                xlapsbutton.connect("toggled", self.on_xlapschange, activity)
                y1gridbutton.connect("toggled", self.on_gridchange, "y1", activity)
                y2gridbutton.connect("toggled", self.on_gridchange, "y2", activity)
                xgridbutton.connect("toggled", self.on_gridchange, "x", activity)
                #Add buttons to frame
                xvbox.pack_start(xdistancebutton, False, True, 0)
                xvbox.pack_start(xtimebutton, False, True, 0)
                xvbox.pack_start(xlapsbutton, False, True, 0)
                xvbox.pack_start(y1gridbutton, False, True, 0)
                xvbox.pack_start(y2gridbutton, False, True, 0)
                xvbox.pack_start(xgridbutton, False, True, 0)
                xFrame.add(xvbox)

                #Populate axis limits frame
                #TODO Need to change these to editable objects and redraw graphs if changed....
                #Create labels etc
                minlabel = Gtk.Label(label="<small>Min</small>")
                minlabel.set_use_markup(True)
                maxlabel = Gtk.Label(label="<small>Max</small>")
                maxlabel.set_use_markup(True)
                xlimlabel = Gtk.Label(label="X")
                limits = {}
                xminlabel = Gtk.Entry(max_length=10)
                xmaxlabel = Gtk.Entry(max_length=10)
                limits['xminlabel'] = xminlabel
                limits['xmaxlabel'] = xmaxlabel
                xminlabel.set_width_chars(5)
                xminlabel.set_alignment(1.0)
                xmaxlabel.set_width_chars(5)
                xmaxlabel.set_alignment(1.0)
                y1limlabel = Gtk.Label(label="Y1")
                y1minlabel = Gtk.Entry(max_length=10)
                y1maxlabel = Gtk.Entry(max_length=10)
                limits['y1minlabel'] = y1minlabel
                limits['y1maxlabel'] = y1maxlabel
                y1minlabel.set_width_chars(5)
                y1minlabel.set_alignment(1.0)
                y1maxlabel.set_width_chars(5)
                y1maxlabel.set_alignment(1.0)
                y2limlabel = Gtk.Label(label="Y2")
                y2minlabel = Gtk.Entry(max_length=10)
                y2maxlabel = Gtk.Entry(max_length=10)
                limits['y2minlabel'] = y2minlabel
                limits['y2maxlabel'] = y2maxlabel
                y2minlabel.set_width_chars(5)
                y2minlabel.set_alignment(1.0)
                y2maxlabel.set_width_chars(5)
                y2maxlabel.set_alignment(1.0)
                resetbutton = Gtk.Button(_('Reset Limits'))
                resetbutton.connect("clicked", self.on_setlimits, activity, True, None)
                setbutton = Gtk.Button(_('Set Limits'))
                setbutton.connect("clicked", self.on_setlimits, activity, False, limits)
                #Add labels etc to table
                limitsbox.attach(minlabel, 1, 2, 0, 1, yoptions=Gtk.AttachOptions.SHRINK)
                limitsbox.attach(maxlabel, 2, 3, 0, 1, yoptions=Gtk.AttachOptions.SHRINK)
                limitsbox.attach(xlimlabel, 0, 1, 1, 2, yoptions=Gtk.AttachOptions.SHRINK)
                limitsbox.attach(xminlabel, 1, 2, 1, 2, yoptions=Gtk.AttachOptions.SHRINK, xpadding=5)
                limitsbox.attach(xmaxlabel, 2, 3, 1, 2, yoptions=Gtk.AttachOptions.SHRINK, xpadding=5)
                limitsbox.attach(y1limlabel, 0, 1, 2, 3, yoptions=Gtk.AttachOptions.SHRINK)
                limitsbox.attach(y1minlabel, 1, 2, 2, 3, yoptions=Gtk.AttachOptions.SHRINK, xpadding=5)
                limitsbox.attach(y1maxlabel, 2, 3, 2, 3, yoptions=Gtk.AttachOptions.SHRINK, xpadding=5)
                limitsbox.attach(y2limlabel, 0, 1, 3, 4, yoptions=Gtk.AttachOptions.SHRINK)
                limitsbox.attach(y2minlabel, 1, 2, 3, 4, yoptions=Gtk.AttachOptions.SHRINK, xpadding=5)
                limitsbox.attach(y2maxlabel, 2, 3, 3, 4, yoptions=Gtk.AttachOptions.SHRINK, xpadding=5)
                limitsbox.attach(setbutton, 0, 3, 4, 5, yoptions=Gtk.AttachOptions.SHRINK)
                limitsbox.attach(resetbutton, 0, 3, 5, 6, yoptions=Gtk.AttachOptions.SHRINK)
                limitsFrame.add(limitsbox)

                row = 0
                if activity.x_axis == "distance":
                    data = activity.distance_data
                elif activity.x_axis == "time":
                    data = activity.time_data
                else:
                    logging.error("x axis is unknown")
                #Sort data
                keys = data.keys()
                keys.sort()
                #Populate Y axis data
                for graphdata in keys:
                    #First Y axis...
                    #Create button
                    y1button = Gtk.CheckButton(label=data[graphdata].title)
                    #Make button active if this data is to be displayed...
                    y1button.set_active(data[graphdata].show_on_y1)
                    #Connect handler for toggle state changes
                    y1button.connect("toggled", self.on_y1change, y1box, graphdata, activity)
                    #Attach button to container
                    y1box.attach(y1button, 0, 1, row, row+1, xoptions=Gtk.AttachOptions.EXPAND|Gtk.AttachOptions.FILL)
                    if data[graphdata].linecolor is not None:
                        #Create a color choser
                        y1color = Gtk.ColorButton()
                        #Set color to current activity color
                        _color = Gdk.color_parse(data[graphdata].linecolor)
                        y1color.set_color(_color)
                        #Connect handler for color state changes
                        y1color.connect("color-set", self.on_y1colorchange, y1box, graphdata, activity)
                        #Attach to container
                        y1box.attach(y1color, 1, 2, row, row+1)
                    else:
                        blanklabel = Gtk.Label(label="")
                        y1box.attach(blanklabel, 1, 2, row, row+1)

                    #Second Y axis
                    y2button = Gtk.CheckButton(label=data[graphdata].title)
                    y2button.set_active(data[graphdata].show_on_y2)
                    y2button.connect("toggled", self.on_y2change, y2box, graphdata, activity)
                    y2box.attach(y2button, 0, 1, row, row+1, xoptions=Gtk.AttachOptions.EXPAND|Gtk.AttachOptions.FILL)
                    if data[graphdata].y2linecolor is not None:
                        y2color = Gtk.ColorButton()
                        _color = Gdk.color_parse(data[graphdata].y2linecolor)
                        y2color.set_color(_color)
                        y2color.connect("color-set", self.on_y2colorchange, y2box, graphdata, activity)
                        #Attach to container
                        y2box.attach(y2color, 1, 2, row, row+1)
                    else:
                        blanklabel = Gtk.Label(label="")
                        y2box.attach(blanklabel, 1, 2, row, row+1)
                    row += 1

                y1Frame.add(y1box)
                y2Frame.add(y2box)
                self.graph_data_hbox.pack_start(xFrame, expand=False, fill=False, padding=5)
                self.graph_data_hbox.pack_start(y1Frame, expand=False, fill=False, padding=5)
                self.graph_data_hbox.pack_start(y2Frame, expand=False, fill=False, padding=5)
                self.graph_data_hbox.pack_start(limitsFrame, expand=False, fill=True, padding=5)
                #self.graph_data_hbox.show_all()
                self.hboxGraphOptions.show_all()
                act = self.grapher.drawActivityGraph(activity=activity, box=self.record_graph_vbox)
                if act.x_limits_u[0] is not None:
                    xmin, xmax = act.x_limits_u
                else:
                    xmin, xmax = act.x_limits
                if act.y1_limits_u[0] is not None:
                    y1min, y1max = act.y1_limits_u
                else:
                    y1min, y1max = act.y1_limits
                if act.y2_limits_u[0] is not None:
                    y2min, y2max = act.y2_limits_u
                else:
                    y2min, y2max = act.y2_limits
                #print y1min, y1max, y2min, y2max
                if xmin is not None and xmax is not None:
                    xminlabel.set_text(str(xmin))
                    xmaxlabel.set_text(str(xmax))
                if y1min is not None and y1max is not None:
                    y1minlabel.set_text(str(y1min))
                    y1maxlabel.set_text(str(y1max))
                if y2min is not None and y2max is not None:
                    y2minlabel.set_text(str(y2min))
                    y2maxlabel.set_text(str(y2max))


                #Default to showing options
                self.buttonGraphShowOptions.hide()
                self.scrolledwindowGraphOptions.show()
                self.buttonGraphHideOptions.show()
        else:
            logging.debug("Activity has no GPX data")
            #Show drop down boxes
            self.hbox30.show()
            #Hide new graph details
            self.graph_data_hbox.hide()
            self.hboxGraphOptions.hide()
            #Remove graph
            vboxChildren = self.record_graph_vbox.get_children()
            logging.debug('Vbox has %d children %s' % (len(vboxChildren), str(vboxChildren) ))
            # ToDo: check why vertical container is shared
            for child in vboxChildren:
                #Remove all FigureCanvasGTK and NavigationToolbar2GTKAgg to stop double ups of graphs
                if isinstance(child, matplotlib.backends.backend_gtk3agg.FigureCanvasGTK3Agg) or isinstance(child, matplotlib.backends.backend_gtk3.NavigationToolbar2GTK3):
                    logging.debug('Removing child: '+str(child))
                    self.record_graph_vbox.remove(child)
            self.record_vbox.set_sensitive(0)
        logging.debug("<<")

    def actualize_heartrategraph(self,activity):
        logging.debug(">>")
        if activity.tracks is not None and len(activity.tracks)>0:
            self.heartrate_vbox_.set_sensitive(1)
            self.drawareaheartrate.drawgraph(activity.tracks)
        else:
            self.heartrate_vbox_.set_sensitive(0)
        logging.debug("<<")

    def actualize_hrview(self,activity):
        logging.debug(">>")
        zones = self.pytrainer_main.profile.getZones()
        record_list = activity.tracks
        is_karvonen_method = self.pytrainer_main.profile.getValue("pytraining","prf_hrzones_karvonen")
        if record_list is not None and len(record_list)>0:
            record_list=record_list[0]
            self.record_zone1.set_text("%s-%s" %(zones[4][0],zones[4][1]))
            self.record_zone2.set_text("%s-%s" %(zones[3][0],zones[3][1]))
            self.record_zone3.set_text("%s-%s" %(zones[2][0],zones[2][1]))
            self.record_zone4.set_text("%s-%s" %(zones[1][0],zones[1][1]))
            self.record_zone5.set_text("%s-%s" %(zones[0][0],zones[0][1]))
            beats = activity.beats
            maxbeats = activity.maxbeats
            self.record_beats.set_text("%0.0f" %beats)
            self.record_maxbeats.set_text("%0.0f" %maxbeats)
            self.record_calories2.set_text("%0.0f" %activity.calories)
            if is_karvonen_method=="True":
                self.record_zonesmethod.set_text(_("Karvonen method"))
            else:
                self.record_zonesmethod.set_text(_("Percentages method"))
        #else:
        #   self.recordview.set_sensitive(0)
        logging.debug("<<")

    def actualize_analytics(self,activity):
        logging.debug(">>")
        record_list = activity.tracks

        def project(d,a):
            return int(a.duration * (d / a.distance)**1.06)

        DISTANCES = {
            .8    : _("800 m"),
            1.5   : _("1500 m"),
            5     : _("5K"),
            7     : _("7K"),
            10    : _("10K"),
            21.1  : _("Half marathon"),
            42.195  : _("Marathon"),
            100   : _("100K"),
        }

        projected_store = Gtk.ListStore(
            GObject.TYPE_STRING,       #id
            GObject.TYPE_STRING,    #name
            GObject.TYPE_STRING,    #distance
            GObject.TYPE_STRING,       #time
            )

        ds = DISTANCES.keys()
        ds = sorted(ds)
        for d in ds:
            v = DISTANCES[d]
            iter = projected_store.append()
            projected_store.set (
                iter,
                0, str(d),
                1, v,
                2, str(d),
                3, str(project(d, activity)),
                )
        self.analyticsTreeView.set_model(projected_store)

        self.analytics_activity = activity
        self.on_change_rank_percentage()

        logging.debug("<<")

    def on_change_rank_percentage(self, widget=None):

        activity = self.analytics_activity
        if widget:
            percentage = widget.get_value() / 100
        else:
            percentage = .05
        records = self.pytrainer_main.ddbb.session.query(Activity).filter(and_(Activity.distance.between(activity.distance * (1-percentage), activity.distance * (1+percentage)), Activity.sport == activity.sport)).all()

        count = 1
        for r in records:
            if r.average > activity.average:
                count += 1

        import numpy
        speeds = [r.average for r in records]
        self.label_ranking_range.set_text("%.2f - %.2f %s" % (self.uc.distance(activity.distance * (1-percentage)), self.uc.distance(activity.distance * (1+percentage)), self.uc.unit_distance))
        self.label_ranking_rank.set_text("%s/%s" % (count, len(records)))
        self.label_ranking_avg.set_text("%.2f %s" % (self.uc.speed(numpy.average(speeds)), self.uc.unit_speed))
        self.label_ranking_speed.set_text("%.2f %s" % (self.uc.speed(activity.average), self.uc.unit_speed))
        self.label_ranking_stddev.set_text("%.4f" % (self.uc.speed(numpy.std(speeds))))
        self.label_ranking_dev.set_text("%+.2fσ" % ((activity.average - numpy.average(speeds)) / numpy.std(speeds)))

        rank_store = Gtk.ListStore(
            GObject.TYPE_INT,       #id
            GObject.TYPE_INT,       #rank
            GObject.TYPE_STRING,    #date
            GObject.TYPE_FLOAT,     #distance
            GObject.TYPE_INT,       #time
            GObject.TYPE_FLOAT,     #speed
            GObject.TYPE_FLOAT,     #pace
            GObject.TYPE_STRING,    #color
            )

        length = len(records)
        rec_set = [0,]
        for r in xrange(max(count-3, 1) if count>1 else count, min(count+3, length-2) if count < length else count):
            rec_set.append(r)
        if length>1 and count!=length:
            rec_set.append(-1)

        for i in rec_set:
            r = records[i]
            iter = rank_store.append()
            rank = length if i==-1 else i+1
            rank_store.set (
                iter,
                0, i,
                1, rank,
                2, str(r.date),
                3, r.distance,
                4, r.duration,
                5, r.average,
                6, r.pace,
                7, '#3AA142' if rank==count else '#000000',
            )

            for c in self.rankingTreeView.get_columns()[:-1]:
                for cr in c.get_cells():
                    if type(cr)==Gtk.CellRendererText:
                        cr.set_property('foreground', 'gray')

        self.rankingTreeView.set_model(rank_store)

    def actualize_dayview(self, date):
        logging.debug(">>")
        self.d_distance_unit.set_text(self.uc.unit_distance)
        self.d_speed_unit.set_text(self.uc.unit_speed)
        self.d_maxspeed_unit.set_text(self.uc.unit_speed)
        self.d_pace_unit.set_text(self.uc.unit_pace)
        self.d_maxpace_unit.set_text(self.uc.unit_pace)
        if self.activeSport:
            sport = self._sport_service.get_sport_by_name(self.activeSport)
        else:
            sport = None
        activity_list = self.pytrainer_main.activitypool.get_activities_for_day(date, sport=sport)

        tbeats, distance, calories, timeinseconds, beats, maxbeats, maxspeed, average, maxpace, pace, totalascent, totaldescent = self._totals_from_activities(activity_list)
        if timeinseconds:
            self.dayview.set_sensitive(1)
        else:
            self.dayview.set_sensitive(0)
        self.day_distance.set_text("%0.2f" %distance)
        hour,min,sec = second2time(timeinseconds)
        self.day_hour.set_text("%d" %hour)
        self.day_minute.set_text("%02d" %min)
        self.day_second.set_text("%02d" %sec)
        if tbeats:
            self.day_beats.set_text("%0.0f" %tbeats)
        else:
            self.day_beats.set_text("")
        self.day_maxbeats.set_text("%0.0f" %maxbeats)
        if average:
            self.day_average.set_text("%0.2f" %average)
        else:
            self.day_average.set_text("")
        self.day_maxspeed.set_text("%0.2f" %maxspeed)
        self.day_pace.set_text("%s" %pace)
        self.day_maxpace.set_text("%s" %maxpace)
        self.day_ascdesc.set_text("%d/%d" %(int(totalascent),int(totaldescent)))
        self.day_calories.set_text("%0.0f" %calories)
        self.day_topic.set_text(str(date))
        logging.debug("<<")

    def actualize_daygraph(self,record_list):
        logging.debug(">>")
        if len(record_list)>0:
            self.day_vbox.set_sensitive(1)
        else:
            self.day_vbox.set_sensitive(0)
        self.drawareaday.drawgraph(record_list)
        logging.debug("<<")

    def actualize_map(self,activity, full_screen=False):
        logging.debug(">>")
        if self.mapviewer and self.mapviewer_fs:
            #Check which type of map viewer to use
            if self.radiobuttonOSM.get_active():
                #Use OSM to draw map
                logging.debug("Using OSM to draw map....")
                from pytrainer.extensions.osm import Osm
                htmlfile = Osm(data_path=self.data_path, waypoint=self.pytrainer_main.waypoint, pytrainer_main=self.parent).drawMap(activity, self.comboMapLineType.get_active())
            elif self.radiobuttonGMap.get_active():
                #Use Google to draw map
                logging.debug("Using Google to draw map")
                from pytrainer.extensions.googlemaps import Googlemaps
                htmlfile = Googlemaps(data_path=self.data_path, waypoint=self.pytrainer_main.waypoint, pytrainer_main=self.parent).drawMap(activity, self.comboMapLineType.get_active())
            else:
                #Unknown map type...
                logging.error("Unknown map viewer requested")
                htmlfile = self.mapviewer.createErrorHtml()
            logging.debug("Displaying htmlfile: %s" % htmlfile)
            if full_screen:
                logging.debug("Displaying in full screen mode")
                self.mapviewer_fs.display_map(htmlfile=htmlfile)
            else:
                logging.debug("Displaying in embedded mode")
                self.mapviewer.display_map(htmlfile=htmlfile)
        logging.debug("<<")

    def actualize_weekview(self, date_range):
        logging.debug(">>")
        self.week_date.set_text("%s - %s (%d)" % (date_range.start_date.strftime("%a %d %b"), date_range.end_date.strftime("%a %d %b"), int(date_range.end_date.strftime("%V"))) )
        if self.activeSport:
            sport = self._sport_service.get_sport_by_name(self.activeSport)
        else:
            sport = None
        activity_list = self.pytrainer_main.activitypool.get_activities_period(date_range, sport=sport)
        tbeats, distance, calories, timeinseconds, beats, maxbeats, maxspeed, average, maxpace, pace, totalascent, totaldescent = self._totals_from_activities(activity_list)
        if timeinseconds:
            self.weekview.set_sensitive(1)
        else:
            self.weekview.set_sensitive(0)

        self.w_distance_unit.set_text(self.uc.unit_distance)
        self.w_speed_unit.set_text(self.uc.unit_speed)
        self.w_maxspeed_unit.set_text(self.uc.unit_speed)
        self.w_pace_unit.set_text(self.uc.unit_pace)
        self.w_maxpace_unit.set_text(self.uc.unit_pace)
        self.weeka_distance.set_text("%0.2f" %distance)
        hour,min,sec = second2time(timeinseconds)
        self.weeka_hour.set_text("%d" %hour)
        self.weeka_minute.set_text("%02d" %min)
        self.weeka_second.set_text("%02d" %sec)
        self.weeka_maxbeats.set_text("%0.0f" %(maxbeats))
        self.weeka_beats.set_text("%0.0f" %(tbeats))
        self.weeka_average.set_text("%0.2f" %average)
        self.weeka_maxspeed.set_text("%0.2f" %maxspeed)
        self.weeka_pace.set_text(pace)
        self.weeka_maxpace.set_text(maxpace)
        self.weeka_ascdesc.set_text("%d/%d" %(int(totalascent),int(totaldescent)))
        self.weeka_calories.set_text("%0.0f" %calories)
        self.weekview.set_sensitive(1)
        self.drawareaweek.drawgraph(activity_list, date_range.start_date)
        logging.debug("<<")

    def actualize_monthview(self, date_range, nameMonth, daysInMonth):
        logging.debug(">>")
        self.month_date.set_text(nameMonth)
        if self.activeSport:
            sport = self._sport_service.get_sport_by_name(self.activeSport)
        else:
            sport = None
        activity_list = self.pytrainer_main.activitypool.get_activities_period(date_range, sport=sport)
        tbeats, distance, calories, timeinseconds, beats, maxbeats, maxspeed, average, maxpace, pace, totalascent, totaldescent = self._totals_from_activities(activity_list)
        if timeinseconds:
            self.monthview.set_sensitive(1)
        else:
            self.monthview.set_sensitive(0)
        self.m_distance_unit.set_text(self.uc.unit_distance)
        self.m_speed_unit.set_text(self.uc.unit_speed)
        self.m_maxspeed_unit.set_text(self.uc.unit_speed)
        self.m_pace_unit.set_text(self.uc.unit_pace)
        self.m_maxpace_unit.set_text(self.uc.unit_pace)

        self.montha_distance.set_text("%0.2f" %distance)
        hour,min,sec = second2time(timeinseconds)
        self.montha_hour.set_text("%d" %hour)
        self.montha_minute.set_text("%02d" %min)
        self.montha_second.set_text("%02d" %sec)
        self.montha_maxbeats.set_text("%0.0f" %(maxbeats))
        self.montha_beats.set_text("%0.0f" %(tbeats))
        self.montha_average.set_text("%0.2f" %average)
        self.montha_maxspeed.set_text("%0.2f" %maxspeed)
        self.montha_pace.set_text(pace)
        self.montha_maxpace.set_text(maxpace)
        self.montha_ascdesc.set_text("%d/%d" %(int(totalascent),int(totaldescent)))
        self.montha_calories.set_text("%0.0f" %calories)
        self.drawareamonth.drawgraph(activity_list, daysInMonth)
        logging.debug("<<")

    def actualize_yearview(self, date_range, year):
        logging.debug(">>")
        self.year_date.set_text("%d" %int(year))
        if self.activeSport:
            sport = self._sport_service.get_sport_by_name(self.activeSport)
        else:
            sport = None
        activity_list = self.pytrainer_main.activitypool.get_activities_period(date_range, sport=sport)
        tbeats, distance, calories, timeinseconds, beats, maxbeats, maxspeed, average, maxpace, pace, totalascent, totaldescent = self._totals_from_activities(activity_list)
        if timeinseconds:
            self.yearview.set_sensitive(1)
        else:
            self.yearview.set_sensitive(0)
            self.drawareayear.drawgraph([])
        self.y_distance_unit.set_text(self.uc.unit_distance)
        self.y_speed_unit.set_text(self.uc.unit_speed)
        self.y_maxspeed_unit.set_text(self.uc.unit_speed)
        self.y_pace_unit.set_text(self.uc.unit_pace)
        self.y_maxpace_unit.set_text(self.uc.unit_pace)
        self.yeara_distance.set_text("%0.2f" %distance)
        hour,min,sec = second2time(timeinseconds)
        self.yeara_hour.set_text("%d" %hour)
        self.yeara_minute.set_text("%02d" %min)
        self.yeara_second.set_text("%02d" %sec)
        self.yeara_beats.set_text("%0.0f" %tbeats)
        self.yeara_maxbeats.set_text("%0.0f" %(maxbeats))
        self.yeara_average.set_text("%0.2f" %average)
        self.yeara_maxspeed.set_text("%0.2f" %maxspeed)
        self.yeara_pace.set_text(pace)
        self.yeara_maxpace.set_text(maxpace)
        self.yeara_ascdesc.set_text("%d/%d " %(totalascent,totaldescent))
        self.yeara_calories.set_text("%0.0f" %calories)
        self.drawareayear.drawgraph(activity_list)
        logging.debug("<<")

    def actualize_athleteview(self, athlete):
        logging.debug(">>")
        self.labelName.set_text(athlete.name)
        self.labelDOB.set_text(athlete.age)
        self.labelHeight.set_text(athlete.height+" cm")

        #Create history treeview
        history_store = Gtk.ListStore(
            GObject.TYPE_INT,       #id
            GObject.TYPE_STRING,    #date
            GObject.TYPE_FLOAT,     #weight
            GObject.TYPE_FLOAT,     #body fat %
            GObject.TYPE_INT,       #resting HR
            GObject.TYPE_INT        #max HR
            )
        for data in athlete.data:
            iter = history_store.append()
            history_store.set (
                iter,
                0, data['id_athletestat'],
                1, str(data['date']),
                2, data['weight'],
                3, data['bodyfat'],
                4, data['restinghr'],
                5, data['maxhr'],
                )
        self.athleteTreeView.set_model(history_store)
        self.grapher.drawAthleteGraph(athlete=athlete, box=self.boxAthleteGraph)
        logging.debug("<<")

    def actualize_statsview(self, stats, record_list):
        logging.debug(">>")
        self.labelTotalDistance.set_text(str(stats.data['total_distance']) + " km")
        self.labelTotalDuration.set_text(str(stats.data['total_duration'] / 3600) + " hours")
        self.labelStartDate.set_text(stats.data['start_date'].strftime('%Y-%m-%d'))
        self.labelEndDate.set_text(stats.data['end_date'].strftime('%Y-%m-%d'))

        data = self.parent.stats.data

        store = Gtk.ListStore(
            GObject.TYPE_INT,
            GObject.TYPE_STRING,
            GObject.TYPE_INT,
            GObject.TYPE_INT,
            GObject.TYPE_FLOAT,
            GObject.TYPE_FLOAT,
            GObject.TYPE_FLOAT,
            GObject.TYPE_INT,
            GObject.TYPE_INT,
            GObject.TYPE_INT,
            GObject.TYPE_FLOAT
            )
        for s in data['sports'].values():
            iter = store.append()

            c = 0
            store.set (iter, c, c)
            c += 1
            store.set (iter, c, s['name'])
            c += 1
            store.set (iter, c, s['count'])
            for f in data['fields'][3:]:
                c += 1
                store.set (iter, c, s['total_'+f])
            c += 1
            if s['total_duration']!=0:    # Avoid division by zero if 0 length sport activity exists in DB
                store.set (iter, c, s['total_distance'] / s['total_duration'] * 3600.)
                for f in data['fields']:
                    c += 1
                    store.set (iter, c, s[f])

        self.statsTreeView.set_model(store)
        self.statsTreeView.set_rules_hint(True)

        store.set_sort_column_id(3, Gtk.SortType.DESCENDING)

        self.drawareatotal.drawgraph(record_list)

        logging.debug("<<")

    def actualize_listview(self,record_list):
        logging.debug(">>")
        #recod list tiene:
        #date,distance,average,title,sports.name,id_record,time,beats,caloriesi
        #Laas columnas son:
        #column_names=[_("id"),_("Title"),_("Date"),_("Distance"),_("Sport"),_("Time"),_("Beats"),_("Average"),("Calories")]
        store = Gtk.ListStore(
            GObject.TYPE_INT,
            GObject.TYPE_STRING,
            GObject.TYPE_STRING,
            GObject.TYPE_FLOAT,
            GObject.TYPE_STRING,
            GObject.TYPE_STRING,
            GObject.TYPE_INT,
            GObject.TYPE_FLOAT,
            GObject.TYPE_INT,
            object)
        for i in record_list:
            try:
                hour,min,sec = second2time(int(i[6]))
            except  (ValueError, TypeError):
                hour,min,sec = (0,0,0)
            _time = "%2d:%02d:%02d" %(hour,min,sec)
            try:
                _id = int(i[5])
            except (ValueError, TypeError) as e:
                logging.debug("Unable to determine id for record: %s" % str(i))
                logging.debug(str(e))
                continue
            _title = i[3]
            _date = str(i[0])
            try:
                _distance = float(i[1])
            except (ValueError, TypeError):
                _distance = 0
            _sport = i[4]
            try:
                _average = float(i[2])
            except (ValueError, TypeError):
                _average = 0
            try:
                _calories = int(i[8])
            except (ValueError, TypeError):
                _calories = 0
            try:
                _beats = round(float(i[7]))
            except (ValueError, TypeError) as e:
                logging.debug("Unable to parse beats for %s" % str(i[7]) )
                logging.debug(str(e))
                _beats = 0.0

            iter = store.append()
            store.set (
                iter,
                0, _id,
                1, _title,
                2, _date,
                3, _distance,
                4, _sport,
                5, _time,
                6, _beats,
                7, _average,
                8, _calories
                )
        #self.allRecordTreeView.set_headers_clickable(True)
        self.allRecordTreeView.set_model(store)
        self.allRecordTreeView.set_rules_hint(True)
        logging.debug("<<")

    def actualize_waypointview(self,record_list,default_waypoint,redrawmap = 1):
        logging.debug(">>")
        #redrawmap: indica si tenemos que refrescar tb el mapa. 1 si 0 no
        #waypoint list tiene:
        #id_waypoint,lat,lon,ele,comment,time,name,sym
        #Laas columnas son:
        #column_names=[_("id"),_("Waypoint")]

        store = Gtk.ListStore(
            GObject.TYPE_INT,
            GObject.TYPE_STRING,
            object)
        iterOne = False
        iterDefault = False
        counter = 0
        default_id = 0
        for i in record_list:
            iter = store.append()
            if not iterOne:
                iterOne = iter
            if int(i[0])==default_waypoint:
                iterDefault = iter
                default_id = counter
            store.set (
                iter,
                0, int(i[0]),
                1, str(i[6])
                )
            counter+=1

        self.waypointTreeView.set_model(store)
        if iterDefault:
            self.waypointTreeView.get_selection().select_iter(iterDefault)
        elif iterOne:
            self.waypointTreeView.get_selection().select_iter(iterOne)
        if len(record_list) > 0:
            self.waypoint_latitude.set_text(str(record_list[default_id][1]))
            self.waypoint_longitude.set_text(str(record_list[default_id][2]))
            self.waypoint_name.set_text(str(record_list[default_id][6]))
            self.waypoint_description.set_text(str(record_list[default_id][4]))
            self.set_waypoint_type(str(record_list[default_id][7]))
        if redrawmap == 1 and self.waypointeditor:
            self.waypointeditor.createHtml(default_waypoint)
            self.waypointeditor.drawMap()
        logging.debug("<<")

    def set_waypoint_type(self, type):
        x = 0
        tree_model = self.waypoint_type.get_model()
        if tree_model is not None:
            #iter = tree_model.get_iter_root()
            for item in tree_model:
                #if isinstance(item, Gtk.TreeModelRow):
                if item[0] == type:
                    self.waypoint_type.set_active(x)
                    return
                x += 1
        self.waypoint_type.insert_text(0, type)
        self.waypoint_type.set_active(0)
        return


    def on_waypointTreeView_button_press(self, treeview, event):
        x = int(event.x)
        y = int(event.y)
        time = event.time
        pthinfo = treeview.get_path_at_pos(x, y)
        if pthinfo is not None:
            path, col, cellx, celly = pthinfo
            treeview.grab_focus()
            treeview.set_cursor(path, col, 0)
            if event.button == 1:
                selected,iter = treeview.get_selection().get_selected()
                id_waypoint=selected.get_value(iter,0)
                self.parent.refreshWaypointView(id_waypoint)
        return False

    def on_listareasearch_clicked(self, widget):
        lisOpt = {
            _("Title"):"title",
            _("Date"):"date",
            _("Distance"):"distance",
            _("Sport"):"sport",
            _("Time"):"time",
            _("Beats"):"beats",
            _("Average"):"average",
            _("Calories"):"calories"
            }
        self.listsearch.title = gtk_str(self.lsa_searchvalue.get_text())
        self.listsearch.sport = self.lsa_sport.get_active()
        self.listsearch.past = self.lsa_past.get_active()
        self.listsearch.duration = self.lsa_duration.get_active()
        self.listsearch.distance = self.lsa_distance.get_active()
        self.parent.refreshListView(self.listsearch.condition)

    def on_listareareset_clicked(self, widget):
        self.listsearch.reset_lsa()
        self.parent.refreshListView(self.listsearch.condition)

    def create_menulist(self,columns):
        for i, column_dict in enumerate(columns):
            if 'visible' in column_dict and not column_dict['visible']:
                pass
            else:
                item = Gtk.CheckMenuItem(column_dict['name'])
                #self.lsa_searchoption.append_text(name)
                item.connect("button_press_event", self.on_menulistview_activate, i)
                self.menulistviewOptions.append(item)
        self.menulistviewOptions.show_all()

    def on_menulistview_activate(self,widget,widget2,widget_position):
        listMenus = {
            0:"title",
            1:"date",
            2:"distance",
            3:"sport",
            4:"time",
            5:"beats",
            6:"average",
            7:"calories" }

        items = self.menulistviewOptions.get_children()
        if items[widget_position-1].get_active():
            newValue = "False"
        else:
            newValue = "True"
        menufile = XMLParser(self.fileconf)
        menufile.setValue("listviewmenu",listMenus[widget_position-1],newValue)
        self.showAllRecordTreeViewColumns()

    def showAllRecordTreeViewColumns(self):
        menufile = XMLParser(self.fileconf)
        listMenus = {
            "id_record":0,
            "title":1,
            "date":2,
            "distance":3,
            "sport":4,
            "time":5,
            "beats":6,
            "average":7,
            "calories":8 }
        columns = self.allRecordTreeView.get_columns()
        menuItems = self.menulistviewOptions.get_children()
        for column in listMenus:
            visible = menufile.getValue("listviewmenu",column)
            if visible == "True":
                visible = True
            else:
                visible = False
            numcolumn = listMenus[column]
            #show the selected columns
            columns[numcolumn].set_visible(visible)
            #select the choice in the menu
            if numcolumn != 0 and self.menublocking != 1:
                menuItems[numcolumn-1].set_active(visible)
        self.menublocking = 1

    def zoom_graph(self, y1limits=None, y1color=None, y1_linewidth=1):
        logging.debug(">>")
        logging.debug("Reseting graph Y axis with ylimits: %s" % str(y1limits) )
        self.drawarearecord.drawgraph(self.record_list,self.laps, y1limits=y1limits, y1color=y1color, y1_linewidth=y1_linewidth)
        logging.debug("<<")

    def update_athlete_item(self, idx, date, weight, bf, restingHR, maxHR):
        logging.debug(">>")
        #Prepare vars
        idx = str(idx)
        date = str(date)
        weight = str(weight)
        bf = str(bf)
        restingHR = str(restingHR)
        maxHR = str(maxHR)
        #Set vars
        self.labelAthleteIdx.set_text(idx)
        self.entryAthleteDate.set_text(date)
        self.entryAthleteWeight.set_text(weight)
        self.entryAthleteBF.set_text(bf)
        self.entryAthleteRestingHR.set_text(restingHR)
        self.entryAthleteMaxHR.set_text(maxHR)
        logging.debug("<<")

    ######################
    ## Lista de eventos ##
    ######################

    def on_xaxischange(self, widget, data=None, activity=None):
        '''Handler for record graph axis selection  changes'''
        if widget.get_active():
            activity.x_axis = data
            self.actualize_recordgraph(activity)

    def on_xlapschange(self, widget, activity=None):
        if widget.get_active():
            activity.show_laps = True
        else:
            activity.show_laps = False
        self.actualize_recordgraph(activity)

    def on_gridchange(self, widget, axis=None, activity=None):
        '''Handler for record graph grid selection changes'''
        if axis == 'y1':
            activity.y1_grid = not activity.y1_grid
        elif axis == 'y2':
            activity.y2_grid = not activity.y2_grid
        elif axis == 'x':
            activity.x_grid = not activity.x_grid
        self.actualize_recordgraph(activity)

    def on_y1colorchange(self, widget, box, graphdata, activity):
        '''Hander for changes to y1 color selection'''
        logging.debug("Setting %s to color %s" % (graphdata, widget.get_color() ) )
        if activity.x_axis == "distance":
            activity.distance_data[graphdata].set_color(str(widget.get_color()))
        elif activity.x_axis == "time":
            activity.time_data[graphdata].set_color(str(widget.get_color()))
        #Replot the activity
        self.actualize_recordgraph(activity)

    def on_y2colorchange(self, widget, box, graphdata, activity):
        '''Hander for changes to y2 color selection'''
        logging.debug("Setting %s to color %s" % (graphdata, widget.get_color() ) )
        if activity.x_axis == "distance":
            activity.distance_data[graphdata].set_color(None, str(widget.get_color()))
        elif activity.x_axis == "time":
            activity.time_data[graphdata].set_color(None, str(widget.get_color()))
        #Replot the activity
        self.actualize_recordgraph(activity)

    def on_y1change(self, widget, box, graphdata, activity):
        '''Hander for changes to y1 selection'''
        logging.debug("Y1 selection toggled: %s" % graphdata)
        #Loop through all options at set data correctly
        for child in box.get_children():
            if activity.x_axis == "distance":
                for item in activity.distance_data:
                    if activity.distance_data[item].title == child.get_label():
                        logging.debug( "Setting %s to %s" % (item, str(child.get_active()) ) )
                        activity.distance_data[item].show_on_y1 = child.get_active()
            elif activity.x_axis == "time":
                for item in activity.time_data:
                    if activity.time_data[item].title == child.get_label():
                        logging.debug( "Setting %s to %s" % (item, str(child.get_active()) ) )
                        activity.time_data[item].show_on_y1 = child.get_active()
        #Replot the activity
        self.actualize_recordgraph(activity)

    def on_y2change(self, widget, box, graphdata, activity):
        '''Hander for changes to y2 selection'''
        logging.debug("Y2 selection toggled: %s" % graphdata)
        #Loop through all options at set data correctly
        for child in box.get_children():
            if activity.x_axis == "distance":
                for item in activity.distance_data:
                    if activity.distance_data[item].title == child.get_label():
                        logging.debug( "Setting %s to %s" % (item, str(child.get_active()) ) )
                        activity.distance_data[item].show_on_y2 = child.get_active()
            elif activity.x_axis == "time":
                for item in activity.time_data:
                    if activity.time_data[item].title == child.get_label():
                        logging.debug( "Setting %s to %s" % (item, str(child.get_active()) ) )
                        activity.time_data[item].show_on_y2 = child.get_active()
        #Replot the activity
        self.actualize_recordgraph(activity)

    def on_setlimits(self, widget, activity, reset, data):
        '''Handler for setting graph limits buttons'''
        if data is None:
            logging.debug("Resetting graph limits...")
            activity.x_limits_u = (None, None)
            activity.y1_limits_u = (None, None)
            activity.y2_limits_u = (None, None)
            #Replot the activity
            self.actualize_recordgraph(activity)
        else:
            #Setting to limits in boxes
            logging.debug("Setting graph limits...")
            #Determine contents of boxes...
            xmin = self._float_or(gtk_str(data['xminlabel'].get_text()), activity.x_limits[0])
            xmax = self._float_or(gtk_str(data['xmaxlabel'].get_text()), activity.x_limits[1])
            y1min = self._float_or(gtk_str(data['y1minlabel'].get_text()), activity.y1_limits[0])
            y1max = self._float_or(gtk_str(data['y1maxlabel'].get_text()), activity.y1_limits[1])
            y2min = self._float_or(gtk_str(data['y2minlabel'].get_text()), activity.y2_limits[0])
            y2max = self._float_or(gtk_str(data['y2maxlabel'].get_text()), activity.y2_limits[1])
            logging.debug("Setting graph limits x: (%s,%s), y1: (%s,%s), y2: (%s,%s)" % (str(xmin), str(xmax), str(y1min), str(y1max), str(y2min), str(y2max)) )
            activity.x_limits_u = (xmin, xmax)
            activity.y1_limits_u = (y1min, y1max)
            activity.y2_limits_u = (y2min, y2max)
            #Replot the activity
            self.actualize_recordgraph(activity)

    def on_window1_configure_event(self, widget, event):
        #print widget #window widget
        #print event # resize event
        self.size = self.window1.get_size()

    def on_buttonShowOptions_clicked(self, widget):
        position_set = self.hpaned1.get_property('position-set')
        if position_set:
            #Currently not showing options - show them
            self.hpaned1.set_property('position-set', False)
            self.buttonShowOptions.set_tooltip_text(_('Hide graph display options') )
        else:
            #Hide options
            self.hpaned1.set_position(0)
            self.buttonShowOptions.set_tooltip_text(_('Show graph display options') )
        #logging.debug('Position: %d' % self.hpaned1.get_position() )
        logging.debug('Position set: %s' % self.hpaned1.get_property('position-set') )

    def on_buttonGraphHideOptions_clicked(self, widget):
        logging.debug('on_buttonGraphHideOptions_clicked')
        self.buttonGraphHideOptions.hide()
        self.scrolledwindowGraphOptions.hide()
        #for child in self.graph_data_hbox.get_children():
        #    if isinstance(child, Gtk.Frame):
        #        child.hide()
        self.buttonGraphShowOptions.show()


    def on_buttonGraphShowOptions_clicked(self, widget):
        logging.debug('on_buttonGraphShowOptions_clicked')
        self.buttonGraphShowOptions.hide()
        #for child in self.graph_data_hbox.get_children():
        #    if isinstance(child, Gtk.Frame):
        #        child.show()
        self.scrolledwindowGraphOptions.show()
        self.buttonGraphHideOptions.show()

    def on_buttonRedrawMap_clicked(self, widget):
        logging.debug('on_buttonRedrawMap_clicked')
        self.parent.refreshMapView()

    def on_radiobuttonMap_toggled(self, widget):
        #Ignore the deselected toggle event
        if widget.get_active() == False:
            return
        logging.debug( 'on_radiobuttonMap_toggled '+ widget.get_name()+ ' activated')
        self.parent.refreshMapView()

    def on_comboMapLineType_changed(self, widget):
        logging.debug( 'on_comboMapLineType_changed '+ widget.get_name()+ ' = ' + str(+ widget.get_active()))
        self.parent.refreshMapView()

    def on_hpaned1_move_handle(self, widget):
        logging.debug("Handler %s", widget)

    def on_spinbuttonY1_value_changed(self, widget):
        y1min = self.spinbuttonY1Min.get_value()
        y1max = self.spinbuttonY1Max.get_value()
        #Check to see if the min and max have the same...
        if y1min == y1max:
            if widget.get_name() == "spinbuttonY1Min": #User was changing the min spinbutton, so move max up
                y1max += 1
            else:   #Move min down
                y1min -= 1
        self.y1_limits=(y1min, y1max)
        self.zoom_graph(y1limits=self.y1_limits, y1color=self.y1_color, y1_linewidth=self.y1_linewidth)

    def on_buttonResetGraph_clicked(self, widget):
        #self.zoom_graph()
        #Reset stored values
        self.y1_limits = None
        self.y1_color = None
        self.y1_linewidth = 1
        self.zoom_graph()

    def on_colorbuttonY1LineColor_color_set(self, widget):
        y1color = widget.get_color()
        cs = y1color.to_string()
        self.y1_color = cs[0:3] + cs[5:7] + cs[9:11]
        self.drawarearecord.drawgraph(self.record_list,self.laps, y1limits=self.y1_limits, y1color=self.y1_color, y1_linewidth=self.y1_linewidth)

    def on_spinbuttonY1LineWeight_value_changed(self, widget):
        self.y1_linewidth = self.spinbuttonY1LineWeight.get_value_as_int()
        self.drawarearecord.drawgraph(self.record_list,self.laps, y1limits=self.y1_limits, y1color=self.y1_color, y1_linewidth=self.y1_linewidth)

    def on_edit_clicked(self,widget):
        selected,iter = self.recordTreeView.get_selection().get_selected()
        id_record = selected.get_value(iter,0)
        self.parent.editRecord(id_record, self.selected_view)

    def on_remove_clicked(self,widget):
        selected,iter = self.recordTreeView.get_selection().get_selected()
        id_record = selected.get_value(iter,0)
        self.parent.removeRecord(id_record)

    def on_export_csv_activate(self,widget):
        self.parent.exportCsv()

    def on_newrecord_clicked(self,widget):
        if self.selected_view  == 'athlete':
            #print 'New athlete'
            self.on_athleteTreeView_edit( None, None)
        else:
            self.parent.newRecord(view=self.selected_view)

    def on_edituser_activate(self,widget):
        self.parent.editProfile()

    def on_calendar_doubleclick(self,widget):
        self.parent.newRecord()

    def on_sportlist_changed(self,widget):
        logging.debug("--")
        if gtk_str(self.sportlist.get_active_text()) != self.activeSport:
            self.activeSport = gtk_str(self.sportlist.get_active_text())
            self.parent.refreshListRecords()
            self.parent.refreshGraphView(self.selected_view)
        else:
            logging.debug("on_sportlist_changed called with no change")

    def on_page_change(self,widget,gpointer,page):
        logging.debug("--")
        if page == 0:
            self.selected_view="record"
        elif page == 1:
            self.selected_view="day"
        elif page == 2:
            self.selected_view="week"
        elif page == 3:
            self.selected_view="month"
        elif page == 4:
            self.selected_view="year"
        elif page == 5:
            self.selected_view="athlete"
        elif page == 6:
            self.selected_view="stats"
        else:
            self.selected_view="record"
        self.parent.refreshGraphView(self.selected_view)

    def on_recordpage_change(self,widget,gpointer,page):
        if page == 0:
            selected_view="info"
        elif page == 1:
            selected_view="graphs"
        elif page == 2:
            selected_view="map"
        elif page == 3:
            selected_view="heartrate"
        elif page == 4:
            selected_view="analytics"
        self.parent.refreshRecordGraphView(selected_view)

    def on_showmap_clicked(self,widget):
        self.infoarea.hide()
        self.maparea.show()
        self.parent.refreshMapView(full_screen=True)

    def on_hidemap_clicked(self,widget):
        self.maparea.hide()
        self.infoarea.show()

    def on_btnShowLaps_toggled(self,widget):
        logging.debug("--")
        self.parent.refreshGraphView(self.selected_view)

    def on_day_combovalue_changed(self,widget):
        logging.debug("--")
        self.parent.refreshGraphView(self.selected_view)

    def on_week_combovalue_changed(self,widget):
        logging.debug("--")
        self.parent.refreshGraphView(self.selected_view)

    def on_month_combovalue_changed(self,widget):
        logging.debug("--")
        self.parent.refreshGraphView(self.selected_view)

    def on_year_combovalue_changed(self,widget):
        logging.debug("--")
        self.parent.refreshGraphView(self.selected_view)

    def on_total_combovalue_changed(self,widget):
        logging.debug("--")
        self.parent.refreshGraphView(self.selected_view)

    def on_calendar_selected(self, widget):
        logging.debug(">>")
        logging.debug("Block (%s) | Selected view: %s" % (self.block, self.selected_view))
        if self.block:
            self.block = False
        else:
            if self.selected_view == "record":
                self.recordview.set_current_page(0)
                self.parent.refreshRecordGraphView("info")
            self.parent.refreshListRecords()
            self.parent.refreshGraphView(self.selected_view)
        logging.debug("<<")

    def on_calendar_changemonth(self,widget):
        logging.debug("--")
        self.block = True
        self.notebook.set_current_page(3)
        self.selected_view="month"
        self.parent.refreshListRecords()
        self.parent.refreshGraphView(self.selected_view)

    def on_calendar_next_year(self,widget):
        logging.debug("--")
        self.block = True
        self.notebook.set_current_page(4)
        self.selected_view="year"
        self.parent.refreshListRecords()
        self.parent.refreshGraphView(self.selected_view)

    def on_classicview_activate(self,widget):
        self.waypointarea.hide()
        self.listarea.hide()
        #self.athletearea.hide()
        self.selected_view = "record"
        self.classicarea.show()

    def on_listview_activate(self,widget):
        self.waypointarea.hide()
        self.classicarea.hide()
        #self.athletearea.hide()
        self.selected_view = "listview"
        #self.parent.refreshListView()
        self.parent.refreshListView(self.listsearch.condition)
        self.listarea.show()

    def on_athleteview_activate(self,widget=None):
        #self.waypointarea.hide()
        #self.classicarea.hide()
        #self.listarea.hide()
        self.parent.refreshAthleteView()
        #self.athletearea.show()

    def on_statsview_activate(self,widget=None):
        self.parent.refreshStatsView()

    def on_waypointsview_activate(self,widget):
        self.listarea.hide()
        self.classicarea.hide()
        #self.athletearea.hide()
        self.parent.refreshWaypointView()
        self.waypointarea.show()

    def on_menu_importdata_activate(self,widget):
        self.parent.importData()

    def on_extensions_activate(self,widget):
        self.parent.editExtensions()

    def on_gpsplugins_activate(self,widget):
        self.parent.editGpsPlugins()
    #hasta aqui revisado

    def on_recordTreeView_button_press_event(self, treeview, event):
        ''' Handler for clicks on recordTreeview list (all records for a day)
            event.button = mouse button pressed (i.e. 1 = left, 3 = right)
        '''
        logging.debug(">>")
        x = int(event.x)
        y = int(event.y)
        time = event.time
        pthinfo = treeview.get_path_at_pos(x, y)
        if pthinfo is not None:
            path, col, cellx, celly = pthinfo
            treeview.grab_focus()
            treeview.set_cursor(path, col, 0)
            if event.button == 3:
                selected,iter = treeview.get_selection().get_selected()
                #Por si hay un registro (malo) sin fecha, pa poder borrarlo
                try:
                    date = self.parent.date.getDate()
                except:
                    date = None
                self.popup.show(selected.get_value(iter,0), event.button, time, date)
            elif event.button == 1:
                self.notebook.set_current_page(0)
                self.parent.refreshGraphView("record")
        logging.debug("<<")
        return False

    def on_allRecordTreeView_button_press(self, treeview, event):
        ''' Handler for clicks on listview list
            event.button = mouse button pressed (i.e. 1 = left, 3 = right)
        '''
        logging.debug(">>")
        x = int(event.x)
        y = int(event.y)
        time = event.time
        pthinfo = treeview.get_path_at_pos(x, y)
        if pthinfo is not None:
            path, col, cellx, celly = pthinfo
            treeview.grab_focus()
            treeview.set_cursor(path, col, 0)
            if event.button == 3:
                selected,iter = treeview.get_selection().get_selected()
                #Por si hay un registro (malo) sin fecha, pa poder borrarlo
                try:
                    date = self.parent.date.getDate()
                except:
                    pass
                self.popup.show(selected.get_value(iter,0), event.button, time, selected.get_value(iter,2))
            elif event.button == 1:
                self.notebook.set_current_page(0)
                self.parent.refreshGraphView("record")
        logging.debug("<<")
        return False

    def actualize_recordTreeView(self, date):
        logging.debug(">>")
        iterOne = False
        store = Gtk.TreeStore(
            GObject.TYPE_INT,           #record_id
            GObject.TYPE_STRING,        #Time
            GObject.TYPE_STRING,        #Sport
            GObject.TYPE_STRING,        #Distance
            object)
        if self.activeSport:
            sport = self._sport_service.get_sport_by_name(self.activeSport)
        else:
            sport = None
        for activity in self.pytrainer_main.activitypool.get_activities_for_day(date, sport=sport):
            iter = store.append(None)
            if not iterOne:
                iterOne = iter
            localTime = activity.date_time.strftime("%H:%M")
            dist = self.uc.distance(activity.distance)
            distance = "%0.2f" % (float(dist) )
            store.set (
                iter,
                0, activity.id,
                1, localTime,
                2, activity.sport.name,
                3, str(distance)  #Needs to be US pref aware....
                )
            for lap in activity.Laps:
                lapNumber = "%s %02d" % (_("lap"), lap.lap_number + 1)
                dist = self.uc.distance(lap.distance)
                distance = "%0.2f" % (float(dist) / 1000.0)
                timeHours = int(lap.duration / 3600)
                timeMin = int((lap.duration / 3600.0 - timeHours) * 60)
                timeSec = lap.duration - (timeHours * 3600) - (timeMin * 60)
                if timeHours > 0:
                    duration = "%d%s%02d%s%02d%s" % (timeHours, _("h"), timeMin, _("m"), timeSec, _("s"))
                else:
                    duration = "%2d%s%02d%s" % (timeMin, _("m"), timeSec, _("s"))

                child_iter = store.append(iter)
                store.set (
                    child_iter,
                    0, activity.id,
                    1, lapNumber,
                    2, duration,
                    3, distance
                    )
                store.set_sort_column_id(1, Gtk.SortType.ASCENDING)
        self.recordTreeView.set_model(store)
        if iterOne:
            self.recordTreeView.get_selection().select_iter(iterOne)
        logging.debug("<<")

    def parseFloat(self,string):
        try:
            return float(string)
        except:
            return float(0)

    def actualize_calendar(self,record_list):
        logging.debug(">>")
        self.calendar.clear_marks()
        #Mark each day that has activity
        for i in record_list:
            self.calendar.mark_day(i)
        #Turn on displaying of week numbers
        display_options = self.calendar.get_display_options()
        self.calendar.set_display_options(display_options|Gtk.CalendarDisplayOptions.SHOW_WEEK_NUMBERS)
        logging.debug("<<")

    def on_about_activate(self,widget):
        if self.aboutwindow is None:
            self.aboutwindow = About(self.data_path, self.version)
            self.aboutwindow.run()
        else:
            self.aboutwindow.present()

    def getSportSelected(self):
        sport = self.sportlist.get_active()
        if (sport > 0):
            return gtk_str(self.sportlist.get_active_text())
        else:
            return None

    def quit(self, *args):
        window_size = "%d, %d" % self.size

        self.pytrainer_main.profile.setValue("pytraining","window_size", window_size)
        self.parent.quit()
        #sys.exit("Exit!")
        #self.parent.webservice.stop()
        #self.gtk_main_quit()

    def on_yearview_clicked(self,widget):
        self.notebook.set_current_page(2)
        self.selected_view="year"
        self.actualize_yearview()

    def on_recordTree_clicked(self,widget,num,num2):
        selected,iter = widget.get_selection().get_selected()
        self.parent.editRecord(selected.get_value(iter,0), self.selected_view)

    ### athleteview events ###
    def on_athleteTreeView_button_press_event(self, treeview, event):
        x = int(event.x)
        y = int(event.y)
        time = event.time
        pthinfo = treeview.get_path_at_pos(x, y)
        if pthinfo is not None:
            path, col, cellx, celly = pthinfo
            treeview.grab_focus()
            treeview.set_cursor(path, col, 0)
            selected,iter = treeview.get_selection().get_selected()
            if event.button == 3:
                #Right mouse button...
                idx = selected.get_value(iter,0)
                date = selected.get_value(iter,1)
                weight = selected.get_value(iter,2)
                bf = selected.get_value(iter,3)
                restingHR = selected.get_value(iter,4)
                maxHR = selected.get_value(iter,5)
                #print "show popup etc (clicked on idx %s, date %s)" % (idx, date)
                #Show popup menu...
                popup = Gtk.Menu()
                #Edit Entry Item
                menuitem = Gtk.MenuItem(label=_("Edit Entry"))
                menuitem.connect("activate", self.on_athleteTreeView_edit, {'id':idx, 'date':date, 'weight':weight, 'bf':bf, 'restingHR':restingHR, 'maxHR':maxHR})
                popup.attach(menuitem, 0, 1, 0, 1)
                #New Entry Item
                menuitem = Gtk.MenuItem(label=_("New Entry"))
                menuitem.connect("activate", self.on_athleteTreeView_edit, None)
                popup.attach(menuitem, 0, 1, 1, 2)
                #Separator
                menuitem = Gtk.SeparatorMenuItem()
                popup.attach(menuitem, 0, 1, 2, 3)
                #Delete Entry Item
                menuitem = Gtk.MenuItem(label=_("Delete Entry"))
                menuitem.connect("activate", self.on_athleteTreeView_delete, idx)
                popup.attach(menuitem, 0, 1, 3, 4)
                popup.show_all()
                popup.popup_at_pointer(None)
            else:
                #Left mouse - so display this row
                pass
                '''
                idx = selected.get_value(iter,0)
                date = selected.get_value(iter,1)
                weight = selected.get_value(iter,2)
                bf = selected.get_value(iter,3)
                restingHR = selected.get_value(iter,4)
                maxHR = selected.get_value(iter,5)
                self.update_athlete_item(idx, date, weight, bf, restingHR, maxHR)'''

    def on_athleteTreeView_edit(self, widget, data):
        logging.debug('>>')
        if data is None:
            #New entry...
            logging.debug('New athlete entry')
            title = _('Create Athlete Entry')
            data = {'id': None, 'date': Date().getDate().strftime("%Y-%m-%d"),
                    'weight': None, 'bf': None, 'restingHR': None, 'maxHR': None}
        else:
            logging.debug('Edit existing athlete entry: %s', str(data))
            title = _('Edit Athlete Entry')
        dialog = Gtk.Dialog(title=title, parent=self.pytrainer_main.windowmain.window1, flags= Gtk.DialogFlags.DESTROY_WITH_PARENT,
                     buttons=(Gtk.STOCK_CANCEL, Gtk.ResponseType.REJECT,
                      Gtk.STOCK_SAVE, Gtk.ResponseType.ACCEPT))
        dialog.set_modal(False)
        #Get Content area of dialog
        vbox = dialog.get_content_area()

        #Build data display
        table = Gtk.Table(1,2)
        self.entryList = []
        #Add date
        label = Gtk.Label(label=_("<b>Date</b>"))
        label.set_use_markup(True)
        entry = Gtk.Entry()
        entry.set_text(data['date'])
        self.entryList.append(entry)
        #Date calander widget
        cal = Gtk.Image()
        cal.set_from_stock(Gtk.STOCK_INDEX, Gtk.IconSize.BUTTON)
        calbut = Gtk.Button()
        calbut.add(cal)
        calbut.connect("clicked", self.on_athletecalendar_clicked)
        table.attach(label,0,1,0,1)
        table.attach(entry,1,2,0,1)
        #table.attach(calbut,2,3,0,1) #TODO

        #Add weight
        label = Gtk.Label(label=_("<b>Weight</b>"))
        label.set_use_markup(True)
        entry = Gtk.Entry()
        if data['weight']:
            entry.set_text(str(round(data['weight'], 2)))
        self.entryList.append(entry)
        table.attach(label,0,1,1,2)
        table.attach(entry,1,2,1,2)
        #Add Body fat
        label = Gtk.Label(label=_("<b>Body Fat</b>"))
        label.set_use_markup(True)
        entry = Gtk.Entry()
        if data['bf']:
            entry.set_text(str(round(data['bf'], 2)))
        self.entryList.append(entry)
        table.attach(label,0,1,2,3)
        table.attach(entry,1,2,2,3)
        #Add Resting HR
        label = Gtk.Label(label=_("<b>Resting Heart Rate</b>"))
        label.set_use_markup(True)
        entry = Gtk.Entry()
        if data['restingHR']:
            entry.set_text(str(data['restingHR']))
        self.entryList.append(entry)
        table.attach(label,0,1,3,4)
        table.attach(entry,1,2,3,4)
        #Add Max HR
        label = Gtk.Label(label=_("<b>Max Heart Rate</b>"))
        label.set_use_markup(True)
        entry = Gtk.Entry()
        if data['maxHR']:
            entry.set_text(str(data['maxHR']))
        self.entryList.append(entry)
        table.attach(label,0,1,4,5)
        table.attach(entry,1,2,4,5)

        vbox.add(table)
        vbox.show_all()
        response = dialog.run()
        #dialog.destroy()
        if response == Gtk.ResponseType.ACCEPT:
            #print "on_athleteTreeView_edit save called", data
            data['date'] = gtk_str(self.entryList[0].get_text())
            data['weight'] = gtk_str(self.entryList[1].get_text())
            data['bf'] = gtk_str(self.entryList[2].get_text())
            data['restingHR'] = gtk_str(self.entryList[3].get_text())
            data['maxHR'] = gtk_str(self.entryList[4].get_text())
            self.on_athleteSave(data)
            logging.debug('Athlete data saved: %s' % str(data))
        dialog.destroy()
        logging.debug('<<')


    def on_athleteTreeView_delete(self, widget, data):
        '''User has opted to delete entry'''
        logging.debug(">>")
        msg = _("Delete this database entry?")
        md = Gtk.MessageDialog(self.pytrainer_main.windowmain.window1, Gtk.DialogFlags.DESTROY_WITH_PARENT, Gtk.MessageType.QUESTION, Gtk.ButtonsType.OK_CANCEL, msg)
        md.set_title(_("Are you sure?"))
        response = md.run()
        md.destroy()
        if response == Gtk.ResponseType.OK:
            logging.debug("User confirmed deletion of athlete entry with id: %s" % data)
            self.pytrainer_main.athlete.delete_record(data)
            self.parent.refreshAthleteView()
        else:
            logging.debug("User canceled athlete record deletion for id %s" % data)
        logging.debug("<<")

    def on_athleteSave(self, data):
        #Get data in fields
        id_athletestat = data['id']
        date = data['date']
        #Check if valid date supplied
        try:
            _date = dateutil.parser.parse(date).date()
        except (ValueError) as e:
            logging.error("Invalid date %s", e)
            return
        weight = data['weight'] or None
        bodyfat = data['bf'] or None
        restinghr = data['restingHR'] or None
        maxhr = data['maxHR'] or None
        #TODO - are any other fields required?

        #Check if an entry has been edited or is a new one
        if id_athletestat is None or id_athletestat == "":
            #New entry
            logging.debug('Creating new entry with values: date %s, weight %s, bodyfat %s, restinghr %s, maxhr %s' % (date, weight, bodyfat, restinghr, maxhr) )
            self.parent.athlete.insert_athlete_stats(date, weight, bodyfat, restinghr, maxhr)
        else:
            #Edited existing entry
            logging.debug('Updating id_athletestat:%s with values: date %s, weight %s, bodyfat %s, restinghr %s, maxhr %s' % (id_athletestat, date, weight, bodyfat, restinghr, maxhr) )
            self.parent.athlete.update_athlete_stats(id_athletestat, date, weight, bodyfat, restinghr, maxhr)
        self.parent.refreshAthleteView()

    def on_athletecalendar_clicked(self,widget):
        logging.debug(">>")
        calendardialog = WindowCalendar(self.data_path,self)
        calendardialog.run()
        logging.debug("<<")

    def setDate(self,date):
        logging.debug(date)
        #self.entryAthleteDate.set_text(date)

    ######## waypoints events ##########
    def on_savewaypoint_clicked(self,widget):
        selected,iter = self.waypointTreeView.get_selection().get_selected()
        id_waypoint = selected.get_value(iter,0)
        lat = gtk_str(self.waypoint_latitude.get_text())
        lon = gtk_str(self.waypoint_longitude.get_text())
        name = gtk_str(self.waypoint_name.get_text())
        desc = gtk_str(self.waypoint_description.get_text())
        sym = gtk_str(self.waypoint_type.get_active_text())
        self.parent.updateWaypoint(id_waypoint,lat,lon,name,desc,sym)

    def on_removewaypoint_clicked(self,widget):
        selected,iter = self.waypointTreeView.get_selection().get_selected()
        id_waypoint = selected.get_value(iter,0)
        self.parent.removeWaypoint(id_waypoint)

    def on_hrpiebutton_clicked(self,widget):
        self.heartrate_vbox2.show()
        self.heartrate_vbox.hide()

    def on_hrplotbutton_clicked(self,widget):
        self.heartrate_vbox.show()
        self.heartrate_vbox2.hide()

    def _totals_from_activities(self, activity_list):
        tbeats = 0
        distance = 0
        calories = 0
        timeinseconds = 0
        beats = 0
        maxbeats = 0
        maxspeed = 0
        average = 0
        maxpace = "0:00"
        pace = "0:00"
        totalascent = 0
        totaldescent = 0
        for activity in activity_list:
            distance += activity.distance
            if activity.calories:
                calories += activity.calories
            timeinseconds += activity.duration
            if activity.upositive:
                totalascent += activity.upositive
            if activity.unegative:
                totaldescent += activity.unegative
            if activity.beats:
                tbeats += activity.beats*(activity.duration/60/60)
            if activity.maxspeed > maxspeed:
                maxspeed = activity.maxspeed
            if activity.maxbeats and activity.maxbeats > maxbeats:
                maxbeats = activity.maxbeats

        distance = self.uc.distance(distance)
        maxspeed = self.uc.speed(maxspeed)

        if tbeats > 0 and timeinseconds > 0:
            tbeats = tbeats/(timeinseconds/60/60)
        if distance > 0 and timeinseconds > 0:
            average = distance/(float(timeinseconds)/60/60)
        if maxspeed > 0:
            maxpace = "%d:%02d" %((3600/maxspeed)/60,(3600/maxspeed)%60)
        if average > 0:
            pace = "%d:%02d" %((3600/average)/60,(3600/average)%60)
        return tbeats, distance, calories, timeinseconds, beats, maxbeats, maxspeed, average, maxpace, pace, totalascent, totaldescent
