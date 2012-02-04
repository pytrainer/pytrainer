# -*- coding: iso-8859-1 -*-

#Copyright (C) Nathan Jones ncjones@users.sourceforge.net

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
from pytrainer.core.equipment import Equipment
from pytrainer.gui.fieldvalidator import PositiveOrZeroIntegerFieldValidator
from pytrainer.gui.fieldvalidator import NotEmptyFieldValidator
from pytrainer.gui.fieldvalidator import EntryInputFieldValidator
from pytrainer.gui.fieldvalidator import EntryValidatorCouple
import logging

class LifeExpentancyFieldValidator(
        PositiveOrZeroIntegerFieldValidator):
    def __init__(self):
        PositiveOrZeroIntegerFieldValidator.__init__(self)
        self.set_allow_empty_field(False)
        self.log_message = 'Invalid life expectancy field entered >>'
        self.error_message = _('Error with the life expectancy field.')

class PriorUsageFieldValidator(
        PositiveOrZeroIntegerFieldValidator):
    def __init__(self):
        PositiveOrZeroIntegerFieldValidator.__init__(self)
        self.set_allow_empty_field(False)
        self.log_message = 'Invalid prior usage field entered >>'
        self.error_message = _('Error with the prior usage field.')

class EquiptmentDescriptionFieldValidator(NotEmptyFieldValidator):
    def __init__(self):
        NotEmptyFieldValidator.__init__(self)
        self.log_message = 'Invalid description field entered >>'
        self.error_message = _('The description field should not be empty.')


class EquipmentStore(gtk.ListStore):
    
    def __init__(self, equipment_service):
        super(EquipmentStore, self).__init__(int, str, float, str, bool)
        self._equipment_service = equipment_service
        for equipment in equipment_service.get_all_equipment():
            self._append_row(equipment)
        self.set_default_sort_func(self._sort)
        self.set_sort_column_id(-1, gtk.SORT_ASCENDING)
        
    def _sort(self, store, x, y):
        if self.get_value(x, 4) != self.get_value(y, 4):
            return self.get_value(y, 4)-self.get_value(x, 4)
        elif self.get_value(x, 2) == self.get_value(y, 2):
            return 0
        else:
            return self.get_value(y, 2)*100-self.get_value(x, 2)*100
    
    def _append_row(self, equipment):
        self.append(self._create_tuple(equipment))
        
    def _create_tuple(self, equipment):
        usage = self._equipment_service.get_equipment_usage(equipment) + equipment.prior_usage
        return(equipment.id,
                equipment.description,
                self._calculate_usage_percent(usage, equipment.life_expectancy),
                str(int(round(usage)))  + " / " + str(equipment.life_expectancy),
                equipment.active)
        
    def _calculate_usage_percent(self, usage, life_expectancy):
        if life_expectancy == 0:
            return 0 
        else:
            return min(100, 100.0 * usage / life_expectancy) 
        
    def add_equipment(self, equipment):
        added_equipment = self._equipment_service.store_equipment(equipment)
        self._append_row(added_equipment)
        
    def get_equipment_item(self, item_path):
        item = None
        if item_path is not None:
            item_id = self.get_value(self.get_iter(item_path), 0)
            item = self._equipment_service.get_equipment_item(item_id)
        return item
        
    def edit_equipment(self, item_path, equipment):
        updated_item = self._equipment_service.store_equipment(equipment)
        for(column_index, value) in enumerate(self._create_tuple(updated_item)):
            self.set(self.get_iter(item_path), column_index, value)
        
    def remove_equipment(self, item_path):
        item = self.get_equipment_item(item_path)
        self._equipment_service.remove_equipment(item)
        self.remove(self.get_iter(item_path))

class EquipmentUi(gtk.HBox):
    
    def __init__(self, glade_conf_dir, equipment_service):
        gtk.HBox.__init__(self)
        self._equipment_store = EquipmentStore(equipment_service)
        self._builder = gtk.Builder()
        self._builder.add_from_file(glade_conf_dir + "/equipment.glade")
        self._init_tree_view()
        self._init_signals()
        self.add(self._get_notebook())
        self.set_property('visible', True)
        
    def _get_notebook(self):
        return self._builder.get_object("notebookEquipment")
    
    def _get_tree_view(self):
        return self._builder.get_object("treeviewEquipmentList")

    def _init_tree_view(self):
        tree_view = self._get_tree_view()
        column = gtk.TreeViewColumn(_("Description"), gtk.CellRendererText(), text=1)
        column.set_resizable(True)
        tree_view.append_column(column)
        tree_view.append_column(gtk.TreeViewColumn(_("Usage"), gtk.CellRendererProgress(), value=2, text=3))
        tree_view.append_column(gtk.TreeViewColumn(_("Active"), gtk.CellRendererToggle(), active=4))
        # add filler column
        tree_view.append_column(gtk.TreeViewColumn())
        tree_view.set_model(self._equipment_store)
        
    def _init_signals(self):
        self._builder.connect_signals({
            "add_equipment_clicked": self._add_equipment_clicked,
            "cancel_add_equipment_clicked": self._cancel_add_equipment_clicked,
            "confirm_add_equipment_clicked": self._confirm_add_equipment_clicked,
            "equipment_cursor_changed": self._equipment_cursor_changed,
            "edit_equipment_clicked": self._edit_equipment_clicked,
            "equipment_row_activated": self._edit_equipment_clicked,
            "cancel_edit_equipment_clicked": self._cancel_edit_equipment_clicked,
            "confirm_edit_equipment_clicked": self._confirm_edit_equipment_clicked,
            "delete_equipment_clicked": self._delete_equipment_clicked,
            "cancel_delete_equipment_clicked": self._cancel_delete_equipment_clicked,
            "confirm_delete_equipment_clicked": self._confirm_delete_equipment_clicked,
            "on_entryEquipmentAddDescription_focus_out_event": self._on_entryEquipmentAddDescription_focus_out_event,
            "on_entryEquipmentAddLifeExpectancy_focus_out_event": self._on_entryEquipmentAddLifeExpectancy_focus_out_event,
            "on_entryEquipmentAddPriorUsage_focus_out_event": self._on_entryEquipmentAddPriorUsage_focus_out_event,
            "on_entryEquipmentEditDescription_focus_out_event": self._on_entryEquipmentEditDescription_focus_out_event,
            "on_entryEquipmentEditLifeExpectancy_focus_out_event": self._on_entryEquipmentEditLifeExpectancy_focus_out_event,
            "on_entryEquipmentEditPriorUsage_focus_out_event": self._on_entryEquipmentEditPriorUsage_focus_out_event,
            "on_entryEquipmentAddLifeExpectancy_insert_text": self._on_entryEquipmentAddLifeExpectancy_insert_text,
            "on_entryEquipmentAddPriorUsage_insert_text": self._on_entryEquipmentAddPriorUsage_insert_text,
            "on_entryEquipmentEditLifeExpectancy_insert_text": self._on_entryEquipmentEditLifeExpectancy_insert_text,
            "on_entryEquipmentEditPriorUsage_insert_text": self._on_entryEquipmentEditPriorUsage_insert_text,
            })
        
    def _get_selected_equipment_path(self):
        (path, _) = self._get_tree_view().get_cursor()
        return path
    
    def _get_selected_equipment_item(self):
        return self._equipment_store.get_equipment_item(self._get_selected_equipment_path())
    
    def clear_add_equipment_fields(self):
        self._builder.get_object("entryEquipmentAddDescription").set_text("") 
        self._builder.get_object("entryEquipmentAddLifeExpectancy").set_text("0")
        self._builder.get_object("entryEquipmentAddPriorUsage").set_text("0")
        self._builder.get_object("checkbuttonEquipmentAddActive").set_active(True)
        self._builder.get_object("textviewEquipmentAddNotes").get_buffer().set_text("")
        # The ok button disabled because there's no description
        self._builder.get_object("buttonEquipmentAddConfirm").set_sensitive(
                False)
        
    def show_page_equipment_list(self):
        self._get_notebook().set_current_page(0)
        
    def show_page_equipment_add(self):
        self._get_notebook().set_current_page(1)
        self._builder.get_object("entryEquipmentAddDescription").grab_focus()
        
    def show_page_equipment_edit(self):
        self._get_notebook().set_current_page(2)
        
    def show_page_equipment_delete(self):
        self._get_notebook().set_current_page(3)
    
    def _add_equipment_clicked(self, widget):
        self.clear_add_equipment_fields()
        self.show_page_equipment_add()
    
    def _cancel_add_equipment_clicked(self, widget):
        self.show_page_equipment_list()
    
    def _confirm_add_equipment_clicked(self, widget):
        #FIXME input validation for numeric fields
        description = self._builder.get_object("entryEquipmentAddDescription").get_text()
        life_expectancy = self._builder.get_object("entryEquipmentAddLifeExpectancy").get_text()
        prior_usage = self._builder.get_object("entryEquipmentAddPriorUsage").get_text()
        active = self._builder.get_object("checkbuttonEquipmentAddActive").get_active()
        notes_buffer = self._builder.get_object("textviewEquipmentAddNotes").get_buffer()
        notes = notes_buffer.get_text(notes_buffer.get_start_iter(), notes_buffer.get_end_iter())
        new_equipment = Equipment()
        new_equipment.description = unicode(description)
        new_equipment.active = active
        new_equipment.life_expectancy = life_expectancy
        new_equipment.prior_usage = prior_usage
        new_equipment.notes = unicode(notes)
        self._equipment_store.add_equipment(new_equipment)
        self.show_page_equipment_list()
        
    def _equipment_cursor_changed(self, widget, *args):
        item_selected = self._get_selected_equipment_item() != None
        self._builder.get_object("buttonEquipmentEdit").set_sensitive(item_selected)
        self._builder.get_object("buttonEquipmentDelete").set_sensitive(item_selected)
    
    def _edit_equipment_clicked(self, widget, *args):
        item = self._get_selected_equipment_item()
        self._builder.get_object("entryEquipmentEditDescription").set_text(item.description)
        self._builder.get_object("entryEquipmentEditLifeExpectancy").set_text(str(item.life_expectancy))
        self._builder.get_object("entryEquipmentEditPriorUsage").set_text(str(item.prior_usage))
        self._builder.get_object("checkbuttonEquipmentEditActive").set_active(item.active)
        if item.notes != None:
            self._builder.get_object("textviewEquipmentEditNotes").get_buffer().set_text(item.notes)
        self.show_page_equipment_edit()
        
    def _cancel_edit_equipment_clicked(self, widget):
        self.show_page_equipment_list()
        
    def _confirm_edit_equipment_clicked(self, widget):
        item = self._get_selected_equipment_item()
        description_text = self._builder.get_object("entryEquipmentEditDescription").get_text()
        item.description = unicode(description_text)
        item.life_expectancy = self._builder.get_object("entryEquipmentEditLifeExpectancy").get_text()
        item.prior_usage = self._builder.get_object("entryEquipmentEditPriorUsage").get_text()
        item.active = self._builder.get_object("checkbuttonEquipmentEditActive").get_active()
        notes_buffer = self._builder.get_object("textviewEquipmentEditNotes").get_buffer()
        notes_text = notes_buffer.get_text(notes_buffer.get_start_iter(), notes_buffer.get_end_iter())
        item.notes = unicode(notes_text)
        self._equipment_store.edit_equipment(self._get_selected_equipment_path(), item)
        self.show_page_equipment_list()
    
    def _delete_equipment_clicked(self, widget):
        self.show_page_equipment_delete()
    
    def _cancel_delete_equipment_clicked(self, widget):
        self.show_page_equipment_list()
    
    def _confirm_delete_equipment_clicked(self, widget):
        self._equipment_store.remove_equipment(self._get_selected_equipment_path())
        self.show_page_equipment_list()

    def _validate_equipment_fields(self, input_fields, label, button):
 
        error_msg = ''
        all_good = True
        for couple in input_fields:
            field = couple._get_entry().get_text()
            validator = couple._get_validator()

            if not validator.validate_field(field):
                error_msg = validator.get_error_message()
                all_good = False

        button.set_sensitive(all_good)
        if error_msg == '':
            msg = ''
        else:
            msg = '<span weight="bold"' + " fgcolor='#ff0000'>" +\
                  str(error_msg) + '</span>'
        label.set_markup(msg)


    def _validate_add_equipment_fields(self):
        input_fields = [
            EntryValidatorCouple(self._builder.get_object( 
                    "entryEquipmentAddLifeExpectancy"),
                LifeExpentancyFieldValidator),
            EntryValidatorCouple(self._builder.get_object(
                        "entryEquipmentAddPriorUsage"),
                PriorUsageFieldValidator),
            EntryValidatorCouple(self._builder.get_object(
                        "entryEquipmentAddDescription"),
                EquiptmentDescriptionFieldValidator),]

        self._validate_equipment_fields(input_fields, 
            self._builder.get_object("label_add_equipment_error_message"),
            self._builder.get_object( "buttonEquipmentAddConfirm"))

    def _validate_edit_equipment_fields(self):
        input_fields = [
            EntryValidatorCouple(self._builder.get_object( 
                    "entryEquipmentEditLifeExpectancy"),
                LifeExpentancyFieldValidator),
            EntryValidatorCouple(self._builder.get_object(
                        "entryEquipmentEditPriorUsage"),
                PriorUsageFieldValidator),
            EntryValidatorCouple(self._builder.get_object(
                        "entryEquipmentEditDescription"),
                EquiptmentDescriptionFieldValidator),]

        self._validate_equipment_fields(input_fields, 
            self._builder.get_object("label_edit_equipment_error_message"),
            self._builder.get_object( "buttonEquipmentEditConfirm"))

    def _validate_field_and_log(self, validator, inputWidget):
        V = validator()
        field = inputWidget.get_text()

        if not V.validate_field(field):
            logging.warning(V.get_log_message() + field + '<<')

    def _on_entryEquipmentAddDescription_focus_out_event(self, widget,
        data):
        self._validate_field_and_log(EquiptmentDescriptionFieldValidator, 
                self._builder.get_object("entryEquipmentAddDescription"))
        self._validate_add_equipment_fields()

    def _on_entryEquipmentAddLifeExpectancy_focus_out_event(self, widget, 
            data):
        self._validate_field_and_log(LifeExpentancyFieldValidator, 
                self._builder.get_object("entryEquipmentAddLifeExpectancy"))
        self._validate_add_equipment_fields()

    def _on_entryEquipmentAddPriorUsage_focus_out_event(self, widget, data):
        self._validate_field_and_log(PriorUsageFieldValidator, 
                self._builder.get_object("entryEquipmentAddPriorUsage"))
        self._validate_add_equipment_fields()

    def _on_entryEquipmentEditDescription_focus_out_event(self, widget,
            data):
        self._validate_field_and_log(EquiptmentDescriptionFieldValidator, 
                self._builder.get_object("entryEquipmentAddDescription"))
        self._validate_edit_equipment_fields()

    def _on_entryEquipmentEditLifeExpectancy_focus_out_event(self, widget, 
            data):
        self._validate_field_and_log(LifeExpentancyFieldValidator, 
                self._builder.get_object("entryEquipmentEditLifeExpectancy"))
        self._validate_edit_equipment_fields()

    def _on_entryEquipmentEditPriorUsage_focus_out_event(self, widget, data):
        self._validate_field_and_log(PriorUsageFieldValidator, 
                self._builder.get_object("entryEquipmentEditPriorUsage"))
        self._validate_edit_equipment_fields()

    def _on_insert_text_positve_integer(self, entry, text, length, 
            input_function):
        V = EntryInputFieldValidator();
        V.validate_entry_input_positive_integer(entry, text, length,
                input_function)

    def _on_entryEquipmentAddLifeExpectancy_insert_text(self, entry, text,
            length, position):
        self._on_insert_text_positve_integer(entry, text, length,
                self._on_entryEquipmentAddLifeExpectancy_insert_text)

    def _on_entryEquipmentAddPriorUsage_insert_text(self, entry, text,
            length, position):
        self._on_insert_text_positve_integer(entry, text, length,
                self._on_entryEquipmentAddPriorUsage_insert_text)

    def _on_entryEquipmentEditLifeExpectancy_insert_text(self, entry, text,
            length, position):
        self._on_insert_text_positve_integer(entry, text, length,
                self._on_entryEquipmentEditLifeExpectancy_insert_text)

    def _on_entryEquipmentEditPriorUsage_insert_text(self, entry, text,
            length, position):
        self._on_insert_text_positve_integer(entry, text, length,
                self._on_entryEquipmentEditPriorUsage_insert_text)

