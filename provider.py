# -*- coding: utf-8 -*-
import xbmcplugin, xbmcgui,urlparse,xbmcaddon
import urllib
import urllib2
import re
import cookielib
import requests
from xbmc import Keyboard
import json
import base64
import utils
import sys
import urlparse

class Provider():
    def __init__(self):
        self._plugin_url = sys.argv[0]
        self._handle = int(sys.argv[1])
        self._params = dict(urlparse.parse_qsl(sys.argv[2].lstrip('?')))
        cookie_jar = cookielib.MozillaCookieJar()
        self._opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookie_jar))
        self._name = "default provider"
        self._cookie_string = self._params["Cookie"] if "Cookie" in self._params else ""
        self._user_agent = self._params["User-Agent"] if "User-Agent" in self._params else ""
        
    def encode_params(self, ps):
        if "User-Agent" not in ps and 'User-Agent' in self._params:
            ps["User-Agent"] = self._params["User-Agent"]
        if "Cookie" not in ps and "Cookie" in self._params:
            ps["Cookie"] = self._params["Cookie"]
        if "url" in ps:
            ps["url"] = base64.urlsafe_b64encode(ps["url"])
        if "title" in ps:
            ps["title"] = base64.urlsafe_b64encode(ps["title"])
        ps["provider"] = self._name
        return urllib.urlencode(ps)
        
    def gen_plugin_url(self, params):
        return self._plugin_url + "?" + self.encode_params(params)
    
    def get_list(self, url):
        pass
        
    def get_movie_url(self, url, movid_id):
        pass
        
    def search(self, movie_name):
        pass
        