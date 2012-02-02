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


class FieldValidator (object):
    """ This is an "abstract" function definition for the method that validates
        an input field in the form.
        The field parameter is a string with the contents of the typed field.
        The method returns a bool indicating whether the field is valid or not.
        
        Python does not really need this definition
        but I think that it makes is clearer for humans."""
    def validate_field (self, field):
        raise NotImplementedError ("Should have implemented validate_field " +
                "the derived classes.")

    def get_log_message (self):
        """ Another "abstract" function definition to provide the log
            message.

            All the "derived" classes should have a log_message attribute
            """
        return self.log_message 

    def get_error_message (self):
        """ Another "abstract" function definition to provide the error
            message.

            All the "derived" classes should have a log_message attribute
            """
        return self.error_message


class PositiveRealNumberFieldValidator (FieldValidator):
    def validate_field (self, field):
        is_valid = False
        if field == '':
            is_valid = True
        else:
            try:
                a = float (field)
                if (a >= 0.0):
                    is_valid = True
            except:
                pass
        return is_valid

class PositiveIntegerFieldValidator (FieldValidator):
    def validate_field (self, field):
        is_valid = False
        if field == '':
            is_valid = True
        else:
            try:
                a = int (field)
                if (a > 0):
                    is_valid = True
            except:
                pass
        return is_valid

class PositiveOrZeroIntegerFieldValidator (FieldValidator):
    def validate_field (self, field):
        # Empty values are not allowed 
        is_valid = False
        try:
            a = int (field)
            if (a >= 0):
                is_valid = True
        except:
            pass
        return is_valid

class DateFieldValidator (FieldValidator):
    def validate_field (self, field):
        is_valid = False

        if field == '':
            is_valid = True
        else:
            try:
                year,month,day = field.split ('-')
                if (len(year) == 4):
                    d = datetime.datetime (int(year), int(month), int (day), \
                            0,0,0)
                    is_valid = True
            except:
                pass

        return is_valid

class NotEmptyFieldValidator (FieldValidator):
    def validate_field(self, field):
        return len (field.strip ()) > 0
