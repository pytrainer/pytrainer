# -*- coding: utf-8 -*-
from unittest import TestCase
from pytrainer.gui.windowrecord import MaxSpeedFieldValidator
from pytrainer.gui.windowrecord import AverageSpeedFieldValidator
from pytrainer.gui.windowrecord import MaxPaceFieldValidator
from pytrainer.gui.windowrecord import AveragePaceFieldValidator
from pytrainer.gui.windowrecord import StartTimeFieldValidator
from pytrainer.gui.windowrecord import DistanceFieldValidator
from pytrainer.gui.windowrecord import AscentFieldValidator
from pytrainer.gui.windowrecord import DescentFieldValidator
from pytrainer.gui.windowrecord import AverageHeartRateFieldValidator
from pytrainer.gui.windowrecord import CaloriesFieldValidator
import gettext


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

class ImportDataFieldValidator(TestCase):

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

    def test_max_speed_field_validator(self):
        good_speed = ['45.0', '0.4', '0.0', '']
        wrong_speed = [ '45.3a', 'a45.3', '-1.3', '-45.3', ]

        V = MaxSpeedFieldValidator()
        self.execute_single_field_validator(V, good_speed, wrong_speed)

    def test_average_speed_field_validator(self):
        good_speed = ['45.0', '0.4', '0.0', '']
        wrong_speed = [ '45.3a', 'a45.3', '-1.3', '-45.3', ]

        V = AverageSpeedFieldValidator()
        self.execute_single_field_validator(V, good_speed, wrong_speed)

    def test_max_pace_field_validator(self):
        good_pace = ['3:05', '3:55', '03:55', '0:00', '']
        wrong_pace = [ '45:3a', 'a45:3', '-1:3', '-45:3', '3.55']

        V = MaxPaceFieldValidator()
        self.execute_single_field_validator(V, good_pace, wrong_pace)

    def test_average_pace_field_validator(self):
        good_pace = ['3:05', '3:55', '03:55', '0:00', '']
        wrong_pace = [ '45:3a', 'a45:3', '-1:3', '-45:3', '3.55']

        V = AveragePaceFieldValidator()
        self.execute_single_field_validator(V, good_pace, wrong_pace)

    def test_start_time_field_validator(self):
        good_time = ['3:05:07', '3:55:07', '03:55:07', '00:00:00']
        wrong_time = [ '10:45:3a', 'a10:45:30', '-10:45:30', '-25:30:00', 
            '3.55.00']

        V = StartTimeFieldValidator()
        self.execute_single_field_validator(V, good_time, wrong_time)

    def test_distance_field_validator(self):
        good_distance = ['45.0', '0.4', '0.0', '']
        wrong_distance = [ '45.3a', 'a45.3', '-1.3', '-45.3', ]

        V = DistanceFieldValidator()
        self.execute_single_field_validator(V, good_distance, wrong_distance)

    def test_ascent_field_validator(self):
        good_ascent = ['45', '0', '']
        wrong_ascent = [ '45a', 'a45', '-1', '-45', '3.77' ]

        V = AscentFieldValidator()
        self.execute_single_field_validator(V, good_ascent, wrong_ascent)

    def test_descent_field_validator(self):
        good_descent = ['45', '0', '']
        wrong_descent = [ '45a', 'a45', '-1', '-45', '3.77' ]

        V = DescentFieldValidator()
        self.execute_single_field_validator(V, good_descent, wrong_descent)

    def test_average_heart_rate_field_validator(self):
        good_rate = ['45', '']
        wrong_rate = [ '45a', 'a45', '-1', '-45', '3.77', '0' ]

        V = AverageHeartRateFieldValidator()
        self.execute_single_field_validator(V, good_rate, wrong_rate)

    def test_calories_field_validator(self):
        good_cal = ['45', '0', '']
        wrong_cal = [ '45a', 'a45', '-1', '-45', '3.77', ]

        V = CaloriesFieldValidator()
        self.execute_single_field_validator(V, good_cal, wrong_cal)
