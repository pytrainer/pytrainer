# -*- coding: utf-8 -*-
from unittest import TestCase

from pytrainer.gui.windowmain import AxisFieldValidatorXMin
from pytrainer.gui.windowmain import AxisFieldValidatorXMax
from pytrainer.gui.windowmain import AxisFieldValidatorY1Min
from pytrainer.gui.windowmain import AxisFieldValidatorY1Max
from pytrainer.gui.windowmain import AxisFieldValidatorY2Min
from pytrainer.gui.windowmain import AxisFieldValidatorY2Max

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


class AxisFieldValidatorsTest(TestCase):
       
    def setUp(self):
        """ These tests are meant to be executed for the source main directory.
            Need to initialize the locale to deal with FieldValidator
            translated error messages. """
        gettext_path =  "./locale"

        gettext.install("pytrainer", gettext_path, unicode=1)


    def tearDown(self):
        pass

    def execute_single_field_validator(self, validator, good_fields,
            wrong_fields):
        for field in good_fields:
            self.assertTrue(validator.validate_field(field))
        for field in wrong_fields:
            self.assertFalse(validator.validate_field(field))

        # Make sure the function is available
        # How do I check the message is right?
        msgErr = validator.get_error_message()
        msgLog = validator.get_log_message()
 
    def test_axis_field_validator_xmin(self):
        good_real_number_fields = ['0.0', '5.1', '-1.1','-5.1', '']
        wrong_real_number_fields = [ '5.1a', 'a5.1', ]

        V = AxisFieldValidatorXMin()
        self.execute_single_field_validator(V, good_real_number_fields,
                wrong_real_number_fields)
