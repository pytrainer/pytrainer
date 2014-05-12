import unittest

from mock import Mock


from pytrainer.test.util.gettext_setup import gettext_setup
gettext_setup()
from pytrainer.record import Record

class RecordTest(unittest.TestCase):
	def setUp(self):
		unittest.TestCase.setUp(self)

		sport_service = Mock()
		parent = Mock()
		self.record = Record(sport_service, data_path=None, parent=parent)

	def test_lapsFromGPX(self):
		gpx_laps = [
			# (elapsedTime, lat, lon, calories, distance, stLat, stLon, intensity, avg_hr, max_hr, max_speed, trigger)
			(300, "48.0", "49.0", "200", "5.0", "48.1", "49.1", "active", 150, 180, 16, "manual"),
			(325, "48.1", "49.1", "200", "5.0", "48.2", "49.2", "active", 151, 185, 15, "manual")
		]

		gpx = Mock()
		gpx.getLaps = Mock(return_value=gpx_laps)

		expected_laps = [
			{'distance': '5.0', 'end_lon': '49.0', 'start_lon': '49.1', 'lap_number': 0, 'calories': '200', 'comments': '', 'laptrigger': 'manual', 'elapsed_time': 300, 'record': '', 'intensity': 'active', 'avg_hr': 150, 'max_hr': 180, 'end_lat': '48.0', 'start_lat': '48.1', 'max_speed': 16},
			{'distance': '5.0', 'end_lon': '49.1', 'start_lon': '49.2', 'lap_number': 1, 'calories': '200', 'comments': '', 'laptrigger': 'manual', 'elapsed_time': 325, 'record': '', 'intensity': 'active', 'avg_hr': 151, 'max_hr': 185, 'end_lat': '48.1', 'start_lat': '48.2', 'max_speed': 15}
		]

		self.assertEqual(self.record.lapsFromGPX(gpx), expected_laps)

	def test_hrFromLaps(self):
		laps = [
			{'elapsed_time': 300, 'avg_hr': 150, 'max_hr': 180},
			{'elapsed_time': 300, 'avg_hr': 160, 'max_hr': 185}
		]

		self.assertEqual(self.record.hrFromLaps(laps), (155, 185))

	def test_hrFromLaps_ponderate_averaging(self):
		laps = [
			{'elapsed_time': 100, 'avg_hr': 150, 'max_hr': 180},
			{'elapsed_time': 300, 'avg_hr': 160, 'max_hr': 185}
		]

		self.assertEqual(self.record.hrFromLaps(laps), (158, 185))

	def test_hrFromLaps_handlingOfNone(self):
		laps = [
			{'elapsed_time': 300, 'avg_hr': None, 'max_hr': 180},
			{'elapsed_time': 300, 'avg_hr': 160, 'max_hr': None}
		]

		self.assertEqual(self.record.hrFromLaps(laps), (160, 180))
