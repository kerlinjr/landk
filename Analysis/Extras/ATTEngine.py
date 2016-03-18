# -*- coding: utf-8 -*-
"""
Created on Thu Feb 25 09:01:17 2016

@author: jrkerlin, Issac Kelly
"""

import json
import requests

class ATTSpeech:
    mydict = json.load(open("C:\\TCDTIMIT\\ATTkeys\\attkeys.txt"))
    CLIENT_ID = mydict['CLIENT_ID']
    CLIENT_SECRET = mydict['CLIENT_SECRET']
    TOKEN = None

    def __init__(self, *args, **kwargs):
        self.get_token()


    def get_token(self):
        # Get Access Token via OAuth.
        # https://matrix.bf.sl.attcompute.com/apps/constellation-sandbox
        response = requests.post("https://api.att.com/oauth/v4/token", {
            "client_id": self.CLIENT_ID,
            "client_secret": self.CLIENT_SECRET,
            "grant_type": "client_credentials",
            "scope": "SPEECH"
        })
        content = json.loads(response.content)
        self.TOKEN = content["access_token"]


    def text_from_file(self, path):

        with open(path, 'rb') as f:
            response = requests.post("https://api.att.com/speech/v3/speechToText",
                headers = {
                    "Authorization": "Bearer %s" % self.TOKEN,
                    "Accept": "application/json",
                    "Content-Type": "audio/wav",
                    "X-SpeechContext": "Generic",
            }, data=f)
        content = json.loads(response.content)
        return content