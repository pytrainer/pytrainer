# -*- coding: iso-8859-1 -*-

#Copyright (C) Rodolfo Gonzalez rgonzalez72@yahoo.com

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

import datetime
import string
import gtk
import gobject


class FieldValidator(object):
    """ This is an "abstract" function definition for the method that validates
        an input field in the form.
        The field parameter is a string with the contents of the typed field.
        The method returns a bool indicating whether the field is valid or not.
        
        Python does not really need this definition
        but I think that it makes is clearer for humans."""
    def validate_field(self, field):
        raise NotImplementedError("Should have implemented validate_field " +
                "the derived classes.")

    def get_log_message(self):
        """ Another "abstract" function definition to provide the log
            message.

            All the "derived" classes should have a log_message attribute
            """
        return self.log_message 

    def get_error_message(self):
        """ Another "abstract" function definition to provide the error
            message.

            All the "derived" classes should have a log_message attribute
            """
        return self.error_message


class RealNumberFieldValidator(FieldValidator):
    def validate_field(self, field):
        is_valid = False
        field_aux = field.strip()
        if field_aux == '':
            is_valid = True
        else:
            try:
                a = float(field.strip())
                is_valid = True
            except:
                pass
        return is_valid

class PositiveRealNumberFieldValidator(FieldValidator):
    def validate_field(self, field):
        is_valid = False
        if field == '':
            is_valid = True
        else:
            try:
                a = float(field)
                if (a >= 0.0):
                    is_valid = True
            except:
                pass
        return is_valid


class PositiveIntegerFieldValidator(FieldValidator):
    def validate_field(self, field):
        is_valid = False
        if field == '':
            is_valid = True
        else:
            try:
                a = int(field)
                if (a > 0):
                    is_valid = True
            except:
                pass
        return is_valid

class PositiveOrZeroIntegerFieldValidator(FieldValidator):
    def validate_field(self, field):
        # Empty values are not allowed 
        is_valid = False
        try:
            a = int(field)
            if(a >= 0):
                is_valid = True
        except:
            pass
        return is_valid

class DateFieldValidator(FieldValidator):
    def validate_field(self, field):
        is_valid = False

        if field == '':
            is_valid = True
        else:
            try:
                year,month,day = field.split('-')
                if(len(year) == 4):
                    d = datetime.datetime(int(year), int(month), int(day), \
                            0,0,0)
                    is_valid = True
            except:
                pass

        return is_valid

class TimeFieldValidator(FieldValidator):
    def validate_field(self, field):
        is_valid = False
        
        try:
            hour,minute,sec = field.split(':')
            hour = int(hour)
            minute = int(minute)
            sec = int(sec)
            if (hour >= 0) and (hour <= 23):
                if (minute >= 0) and (minute <= 59):
                    if (sec >= 0) and (sec <= 59):
                        is_valid = True
        except:
            pass

        return is_valid

class NotEmptyFieldValidator(FieldValidator):
    def validate_field(self, field):
        return len(field.strip()) > 0

class WeightFieldValidator(PositiveRealNumberFieldValidator):
    def __init__(self):
        self.log_message = 'Invalid weight field entered >>'
        self.error_message = _('Error with the weight field.')

class MaxHeartRateFieldValidator(PositiveIntegerFieldValidator):
    def __init__(self):
        self.log_message = 'Invalid maximum heart rate field entered >>'
        self.error_message = _('Error with the maximum heart rate field.')

class RestHeartRateFieldValidator(PositiveIntegerFieldValidator):
    def __init__(self):
        self.log_message = 'Invalid resting heart rate field entered >>'
        self.error_message = _('Error with the resting heart rate field.')

class DateEntryFieldValidator(DateFieldValidator):
    def __init__(self):
        self.log_message = 'Invalid date field entered >>'
        self.error_message = _('Error with the date field.')

class EntryInputFieldValidator(object):
    """A class to check the allowed characters on an entry form.
     
     The methods in this class are meant to be called within a 'insert_text'
     signal callback function.
    """
    def filter_entry_input(self, entry, text, length, insert_function,
            allowed_chars):
        """ The insert_function parameter is the function that deals with 
            signal. """
        position = entry.get_position()
        result = ''.join([c for c in text if c in allowed_chars])
        if result != '':
            # Block the callback to avoid calling the function recursively
            entry.handler_block_by_func(insert_function)
            entry.insert_text(result, position)
            entry.handler_unblock_by_func(insert_function)

            # Set the cursor in the right position
            new_pos = position + len(result)
            gobject.idle_add(entry.set_position, new_pos)
        else:
            # Beep to show the error
            gtk.gdk.beep()
        entry.stop_emission("insert_text")

    def validate_entry_input_positive_integer(self, entry, text, length,
            insert_function):
        allowed_chars = string.digits
        self.filter_entry_input( entry, text, length, insert_function,
                allowed_chars)
 
    def validate_entry_input_date(self, entry, text, length, insert_function):
        allowed_chars = string.digits + '-'
        self.filter_entry_input( entry, text, length, insert_function,
                allowed_chars)

    def validate_entry_input_positive_real_number(self, entry, text, length,
            insert_function):
        allowed_chars = string.digits + '.'
        self.filter_entry_input( entry, text, length, insert_function,
                allowed_chars)

    def validate_entry_input_real_number(self, entry, text, length,
            insert_function):
        allowed_chars = string.digits + '.-'
        self.filter_entry_input( entry, text, length, insert_function,
                allowed_chars)

class EntryValidatorCouple(object):
    """ This class relates an entry object with a validator. 
        It's used in the profiles forms to validate the entries.
        """
    def __init__(self, entry, validator):
        self.entry = entry
        self.validator = validator()

    def _get_entry(self):
        return self.entry

    def _get_validator(self):
        return self.validator


