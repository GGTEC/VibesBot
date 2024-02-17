# -*- coding: utf-8 -*-
import json

class auth_data:
    def __init__(self, filename):
        with open(filename) as f:
            self.data = json.load(f)

    def USERNAME(self):
        return self.data['USERNAME']
    
    def SESSIONID(self):
        return self.data['SESSIONID']