#!/usr/bin/env python

import unittest
from time import sleep
from stravaupload import ProgressDialog

class ProgressDialogTest(unittest.TestCase):
    def testProgress(self):
        with ProgressDialog() as p:
            sleep(5)
        print "after: %s" % p.progress.poll()
        self.assert_(p.progress.poll() is not None, 'zenity still running!')
        
if __name__ == '__main__':
    unittest.main()
