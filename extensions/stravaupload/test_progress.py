import unittest
from time import sleep
from stravaupload import ProgressDialog

class ProgressDialogTest(unittest.TestCase):
    """ nose-compatible test to drive the class that wraps up
        zentity.  Ensures the zenity process is closed correctly. 
        
        Not part of the larger test cases as extensions are
        not installed as importable modules without modifying
        the path.
        
        Run 'nosetests extensions' from the project root to test. """
    def test_progress_process_closes_cleanly(self):
        with ProgressDialog() as p:
            sleep(2)
        self.assert_(p.progress.poll() is not None, 'zenity still running!')
        
