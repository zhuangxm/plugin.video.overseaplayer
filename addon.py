# -*- coding: utf-8 -*-

## using zip -r -0 oversea.zip plugin.video.overseaPlayer/ to zip

import xbmcplugin, xbmcgui,urlparse,xbmcaddon
from xbmc import Keyboard
import urllib
import urllib2
import cookielib
import re
import base64

headers = {"Host": "www.olevod.com",
"Cache-Control": "nax-age=0",
"Accept": "application/json, text/plain, */*",
"Origin": "https://www.olevod.com",
"X-Requested-With": "XMLHttpRequest",
"User-Agent": 'Mozilla/5.0 (iPad; CPU OS 6_0 like Mac OS X) AppleWebKit/536.26 (KHTML, like Gecko) Version/6.0 Mobile/10A5376e Safari/8536.25',
"Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
"DNT": "1",
"Referer": "https://www.olevod.com",
"Accept-Encoding": "",
"Accept-Language": "de-DE,de;q=0.8,en-US;q=0.6,en;q=0.4,zh-CN;q=0.2,zh;q=0.2,zh-TW;q=0.2,fr-FR;q=0.2,fr;q=0.2",
"Connection": "keep-alive"}

baseUrl = "https://www.olevod.com"


addon = xbmcaddon.Addon(id='plugin.video.overseaPlayer')
__language__ = addon.getLocalizedString
plugin_url = sys.argv[0]
handle = int(sys.argv[1])
params = dict(urlparse.parse_qsl(sys.argv[2].lstrip('?')))
cookie = cookielib.MozillaCookieJar()
opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookie))
#indexRequest = urllib2.Request(baseUrl, None, headers)
#opener.open(indexRequest)

def parse(content, reg):
    pattern = re.compile(reg)
    return pattern.findall(content)

def Index():
    for item in ["Movie", "Tv", "Search"]:
        listitem=xbmcgui.ListItem(item)
        isFolder=True
        url = plugin_url + '?act='+ item + '&name=' + item
        xbmcplugin.addDirectoryItem(handle,url,listitem,isFolder)
    xbmcplugin.endOfDirectory(handle)
    
def getMovieList(url):
    url = baseUrl + url
    req = urllib2.Request(url, None, headers)
    result = opener.open(req).read()
    reg = r'<a href="(.*?)" class=".*?">\n<img.*?data-original="(.*?)".*?alt="(.*?)".*?/>'
    playList = parse(result, reg)
    print("playlist:", playList)
    for i in playList:
        imageUrl = baseUrl + i[1]
        listitem = xbmcgui.ListItem(i[2],thumbnailImage=imageUrl)
        url=sys.argv[0]+'?act=Detail&url='+base64.urlsafe_b64encode(i[0])+'&title='+base64.urlsafe_b64encode(i[2])
        xbmcplugin.addDirectoryItem(handle, url, listitem, True)
    xbmcplugin.endOfDirectory(handle)
        
    
def Movie():
    getMovieList('/?m=vod-type-id-1.html')
    
def Tv():
    getMovieList('/?m=vod-type-id-2.html')
    
def Search():
    kb = Keyboard('',u'Please input Movie or TV Shows name 请输入想要观看的电影或电视剧名称')
    kb.doModal()
    if not kb.isConfirmed(): return
    sstr = kb.getText()
    if not sstr: return
    inputMovieName=urllib.quote_plus(sstr)

    urlSearch = baseUrl + '/index.php?m=vod-search'
    data = 'wd='+inputMovieName
    req = urllib2.Request(urlSearch, data, headers)
    searchResponse = opener.open(req).read()
    
    searchReg = r'<h6 class="fl">.*?<a href="(.*?)".*?>(.*?)</a>'
    searchResult = parse(searchResponse, searchReg)
    
    listitem = xbmcgui.ListItem('[COLOR FFFF00FF]Search result 当前搜索: [/COLOR][COLOR FFFFFF00]('+sstr+') [/COLOR][COLOR FF00FFFF] Total 共计：'+str(len(searchResult))+'[/COLOR]【[COLOR FF00FF00]'+'Click here for new search 点此输入新搜索内容'+'[/COLOR]】')
    url=sys.argv[0]+'?act=Search'
    xbmcplugin.addDirectoryItem(handle, url, listitem, True)
    for i in searchResult:
        listitem = xbmcgui.ListItem(i[1])
        url=sys.argv[0]+'?act=Detail&url='+base64.urlsafe_b64encode(i[0])+'&title='+base64.urlsafe_b64encode(i[1])
        xbmcplugin.addDirectoryItem(handle, url, listitem, True)
    xbmcplugin.endOfDirectory(handle)


def Episodes():
    url = base64.urlsafe_b64decode(params['url'])
    title = base64.urlsafe_b64decode(params['title'])
    urlDetail = baseUrl + url
    req = urllib2.Request(urlDetail, None, headers)
    response = opener.open(req).read()
    reg = r'<li><a href="(.*?)".*?>(.*?)</a>'
    pattern = re.compile(reg)
    result = pattern.findall(response)
    for i in range(len(result)):
        item = result[i]
        episodeTitle = title + " " + item[1]
        listitem = xbmcgui.ListItem(episodeTitle)
        listitem.setInfo("video", {"Title": episodeTitle})
        listitem.setProperty("IsPlayable","true")
        url=sys.argv[0]+'?act=Play&url='+base64.urlsafe_b64encode(item[0])+'&title='+ base64.urlsafe_b64encode(episodeTitle)
        xbmcplugin.addDirectoryItem(handle, url, listitem, False)
    xbmcplugin.endOfDirectory(handle)
    
def play_url(url, title):
    playlist = xbmc.PlayList(1)
    playlist.clear()
    listitem=xbmcgui.ListItem(title)
    playlist.add(url, listitem=listitem)
    #xbmc.Player().play(playlist)
    #xbmc.Player().play(url, listitem)
    xbmcplugin.setResolvedUrl(handle, succeeded=True, listitem=listitem)
    
def Play():
    url = base64.urlsafe_b64decode(params['url'])
    title = base64.urlsafe_b64decode(params['title'])
    
    urlPlay = baseUrl + url
    req = urllib2.Request(urlPlay, None, headers)
    response = opener.open(req).read()
    reg = r'var url=\'(.*?)\'.*?replace\(\'(.*?)\'.*?\'(.*?)\''
    pattern = re.compile(reg)
    result = pattern.findall(response)
    print result
    url = result[0][0].replace(result[0][1],result[0][2])
    print url
    play_url(url, title)
    
{
    'Index': Index,
    'Movie': Movie,
    "Tv": Tv,
    'Search': Search,
    'Detail': Episodes,
    'Play': Play
}[params.get('act', 'Index')]()