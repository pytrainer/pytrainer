import unittest
from pytrainer.lib.ddbb import DDBB


class DDBBTestCase(unittest.TestCase):
    CREATE_DEFAULT_DATA = True

    def setUp(self):
        self.ddbb = DDBB()
        self.ddbb.create_tables(add_default=self.CREATE_DEFAULT_DATA)
        self.ddbb.connect()
        self.session = self.ddbb.sessionmaker()

    def tearDown(self):
        self.session.close()
        self.ddbb.disconnect()
        self.ddbb.drop_tables()
