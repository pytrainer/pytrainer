#!/usr/bin/env python 

import json
import subprocess

class StravaUpload:
    def __init__(self, parent = None, pytrainer_main = None, conf_dir = None, options = None):
        self.gpxfile = None
        self.pytrainer_main = pytrainer_main
        self.conf_dir = conf_dir

        self.login_url = "https://www.strava.com/api/v2/authentication/login"
        self.upload_url = "http://www.strava.com/api/v2/upload"

        self.email = ""
        self.password = ""

    def login_token(self):
        token = None
        try:
            # TODO: use conf_dir?
            with open('.strava_token') as f:
                token = f.readline()
        except:
            pass
        if token is None or token.strip() == '' :
            # file doesn't exist, or failed to read it so attempt login
            cmd = ["curl", "-s", "-X", "POST", "-d", ("email=%s" % self.email), "-d", ("password=%s" % self.password), self.login_url]
            result = json.loads(subprocess.check_output(cmd));
            token = result['token']
            try:
                f = open('.strava_token', 'w')
                f.write(token)
            finally:
                f.close()
        return token 

    def upload(self, token):
        # TODO: the remining bits of the method using the login token
        #       refactor json handling to pull requested item e.g. get('token'), get('success')
        return True

    def run(self):
        # only prints token so far ;)
        self.log = "Strava Upload "
        try:
            result = self.login_token();
            if result is not None:
                print result
        except (ValueError, KeyError), e:
            self.log = self.log + ("JSON error: %s.  Username and password correct?" % e)
        except Exception, e:
            self.log = self.log + "failed! %s" % e
        else:
            self.log = self.log + "success!"
        print self.log

# TODO: remove this
if __name__ == '__main__':
    app = StravaUpload()
    app.run()
