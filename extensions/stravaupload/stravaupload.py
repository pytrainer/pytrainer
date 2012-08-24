#!/usr/bin/env python 

import json
import subprocess

class StravaUpload:
    def __init__(self, parent = None, pytrainer_main = None, conf_dir = None, options = None):
        self.gpxfile = None
        self.pytrainer_main = pytrainer_main
        self.conf_dir = conf_dir

        self.login_url = "https://www.strava.com/api/v2/authentication/login"

        self.email = ""
        self.password = ""

    def login_token(self):
        cmd = ["curl", "-s", "-X", "POST", "-d", ("email=%s" % self.email), "-d", ("password=%s" % self.password), self.login_url]
        output = subprocess.check_output(cmd)
        return output 

    def upload(self, token):
        # TODO: the remining bits of the method using the login token
        #       refactor json handling to pull requested item e.g. get('token'), get('success')
        return True

    def run(self):
        # only prints token so far ;)
        self.log = "Strava Upload "
        try:
            result = json.loads(self.login_token());
            if result is not None:
                print result['token']
        except (ValueError, KeyError), e:
            self.log = self.log + ("JSON error: %s.  Username and password correct?" % e)
        except:
            self.log = self.log + "failed!"
        else:
            self.log = self.log + "success!"
        print self.log

if __name__ == '__main__':
    app = StravaUpload()
    app.run()
