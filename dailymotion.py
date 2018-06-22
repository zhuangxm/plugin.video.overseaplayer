#!/usr/bin/python
# -*- coding: utf-8 -*-
import urllib
import urllib2
import xbmcplugin
import xbmcaddon
import xbmcgui
import sys
import os
import re
import json
import base64
import datetime
import unicodedata
import requests
import pickle
from operator import itemgetter
from HTMLParser import HTMLParser


maxVideoQuality = "1080"

def split_url(s):
    s = s.splitlines()[-1]
    s = s.split('#cell')[0]
    return s

def qualities(video):
    if video[0] == "auto":
        return 0
    else:
        return int(video[0])

def getStreamUrl(id,live=False):
    ff = "off"
    language = "en_US"
    #print 'The url is ::',url
    headers = {'User-Agent':'Android'}
    cookie = {'Cookie':"lang="+language+"; ff="+ff}
    r = requests.get("http://www.dailymotion.com/player/metadata/video/"+id,headers=headers,cookies=cookie)
    #print("r headers:",r.headers)
    content = r.json()
    #print("content:", content)
    if content.get('error') is not None:
        Error = (content['error']['title'])
        xbmc.executebuiltin('XBMC.Notification(Info:,'+ Error +' ,5000)')
        return
    else:
        cc= content['qualities']

        cc = cc.items()

        #cc = sorted(cc,key=s,reverse=True)
        cc = sorted(cc,reverse=True, key=qualities)
        m_url = ''
        other_playable_url = []

        for source,json_source in cc:
            source = source.split("@")[0]
            
            for item in json_source:
            
                m_url = item.get('url',None)
                #xbmc.log("DAILYMOTION - m_url = %s" %m_url,xbmc.LOGNOTICE)
                if m_url:
                    if not live:

                        if source == "auto" :
                            continue

                        elif  int(source) <= int(maxVideoQuality) :
                            if 'video' in item.get('type',None):
                                return m_url

                        elif '.mnft' in m_url:
                            continue
                         
                    else:
                        if '.m3u8?auth' in m_url:
                            m_url = m_url.split('?auth=')
                            the_url = m_url[0] + '?redirect=0&auth=' + urllib.quote(m_url[1])
                            rr = requests.get(the_url,cookies=r.cookies.get_dict() ,headers=headers)
                            #print("rr-headers:", rr.headers)
                            #print("rr-text:", rr.text)
                            return split_url(rr.text)
                            if rr.headers.get('set-cookie'):
                                print 'adding cookie to url'
                                return split_url(rr.text)+'|Cookie='+rr.headers['set-cookie']
                            else:
                                return split_url(rr.text)
                    other_playable_url.append(m_url)
                    
        if len(other_playable_url) >0: # probably not needed, only for last resort
            for m_url in other_playable_url:
                #xbmc.log("DAILYMOTION - other m_url = %s" %m_url,xbmc.LOGNOTICE)
                if '.m3u8?auth' in m_url:
                    rr = requests.get(m_url,cookies=r.cookies.get_dict() ,headers=headers)
                    #print("hello", rr.headers)
                    #print("hello, rr-text:", rr.text)
                    if rr.headers.get('set-cookie'):
                        print 'adding cookie to url'
                        strurl = re.findall('(http.+)',rr.text)[0].split('#cell')[0]+'|Cookie='+rr.headers['set-cookie']
                    else:
                        strurl = re.findall('(http.+)',rr.text)[0].split('#cell')[0]
                    #xbmc.log("DAILYMOTION - Calculated url = %s" %strurl,xbmc.LOGNOTICE)
                    return strurl
