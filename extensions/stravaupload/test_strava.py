import unittest, os
from time import sleep
from stravaupload import ProgressDialog, StravaUpload

class StravaUploadTest(unittest.TestCase):
    """ nose-compatible test to drive the class that wraps up
        zenity.  Ensures the zenity process is closed correctly. 
        
        Not part of the larger test cases as extensions are
        not installed as importable modules without modifying
        the path.
        
        Run 'nosetests extensions' from the project root to test. """
    def tearDown(self):
        try:
            os.remove('./.strava_uploads')
        except:
            pass

    def test_progress_process_closes_cleanly(self):
        with ProgressDialog("testing") as p:
            sleep(2)
        self.assert_(p.progress.poll() is not None, 'zenity still running!')

    def test_store_upload_id(self):
        with StravaUpload(None, None, '.', None) as app:
            app.store_upload_id(1, 12345)
        exists = False
        try:
            with open(app.strava_uploads) as f:
                exists = True
        except:
            pass
        self.assert_(exists is True, 'Store upload token failed')
        
