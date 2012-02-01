# -*- coding: utf-8 -*-
from unittest import  TestCase
from pytrainer.gui import fieldvalidator 


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

class FieldValidatorTest (TestCase):
    def setUp (self):
        pass

    def tearDown (self):
        pass

    def execute_validations (self, validator, good_fields, wrong_fields):
        for field in good_fields:
            self.assertTrue (validator.validate_field (field))

        for field in wrong_fields:
            self.assertFalse (validator.validate_field(field))

    def test_positive_real_number_field_validator (self):
        good_real_number_fields = ['0.0', '5.1', '']
        wrong_real_number_fields = [ '5.1a', 'a5.1', '-1.1', '-5.1',  ]

        V = fieldvalidator.PositiveRealNumberFieldValidator ()
        self.execute_validations (V, good_real_number_fields,
                wrong_real_number_fields)

    def test_positive_integer_field_validator (self):
        good_integer_fields = ['1', '22', '']
        wrong_integer_fields = ['45a', 'a45', '0', '-1', '-45']
        V = fieldvalidator.PositiveIntegerFieldValidator ()
        self.execute_validations (V, good_integer_fields, wrong_integer_fields)

    def test_positive_or_zero_integer_field_validator (self):
        good_integer_fields = ['1', '22', '0', '']
        wrong_integer_fields = ['45a', 'a45', '-1', '-45']
        V = fieldvalidator.PositiveOrZeroIntegerFieldValidator ()
        self.execute_validations (V, good_integer_fields, wrong_integer_fields)
