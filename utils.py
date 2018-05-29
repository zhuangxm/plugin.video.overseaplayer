# -*- coding: utf-8 -*-
import re
from bs4 import BeautifulSoup
import xbmc, xbmcgui
import urllib
import sys

headers = {"Host": "www.olevod.com",
"Cache-Control": "nax-age=0",
"Accept": "application/json, text/plain, */*",
#"Origin": "https://www.olevod.com",
"X-Requested-With": "XMLHttpRequest",
"User-Agent": 'Mozilla/5.0 (iPad; CPU OS 6_0 like Mac OS X) AppleWebKit/536.26 (KHTML, like Gecko) Version/6.0 Mobile/10A5376e Safari/8536.25',
"Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
"DNT": "1",
"Referer": "https://www.olevod.com",
"Accept-Encoding": "",
"Accept-Language": "de-DE,de;q=0.8,en-US;q=0.6,en;q=0.4,zh-CN;q=0.2,zh;q=0.2,zh-TW;q=0.2,fr-FR;q=0.2,fr;q=0.2",
"Connection": "keep-alive"}

def custom_header(host, protocol, refers = ""):
    new_header = headers.copy()
    new_header["Host"] = host
    #new_header["Origin"] = protocol + "://" + host
    url = protocol + "://" + host
    if len(refers) == 0:
        new_header["Referer"] = url
    else:
        new_header["Referer"] = refers 
    return new_header      
        
        
def parseHtml(html_doc):
    return BeautifulSoup(html_doc, 'html.parser')
    
def parse(content, reg):
    pattern = re.compile(reg, re.DOTALL)
    return pattern.findall(content)
    
def xbmc_play(url , title):
    listitem=xbmcgui.ListItem(title, path = url)
    xbmc.Player().play(url, listitem)

    
