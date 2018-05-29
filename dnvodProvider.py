# -*- coding: utf-8 -*-

from provider import *

import utils
import cfscrape
import xbmcplugin
from xbmc import Keyboard
import xbmc

class DnvodProvider(Provider):
    def __init__(self):
        Provider.__init__(self)
        self._header = utils.custom_header("www.dnvod.tv", "http", "http://www.dnvod.tv")
        self._baseUrl = "http://www.dnvod.tv"
        self._name = "dnvod"
        if len(self._cookie_string) > 0:
            self._header['Cookie'] = self._cookie_string
        if len(self._user_agent) > 0:
            self._header['User-Agent'] = self._user_agent
        
    def index(self):
        for key, value in {"search": "load_search"}.iteritems():
            listitem=xbmcgui.ListItem(key)
            isFolder=True
            url = self.gen_plugin_url({"act": value,
                                       "name": value})
            xbmcplugin.addDirectoryItem(self._handle,url,listitem,isFolder)
        xbmcplugin.endOfDirectory(self._handle)
        
    def getMovieList(self, url):
        url = self._baseUrl + url
        print("getMoveList url", url)
        print self._header
        req = urllib2.Request(url, None, self._header)
        result = self._opener.open(req).read()
        #print result
        reg = r'<a href="([-a-zA-Z0-9@:%_\+.~#?&//=]*?)" class=".*?">\n<img.*?data-original="(.*?)".*?alt="(.*?)".*?/>'
        playList = utils.parse(result, reg)
        print("playlist:", playList)
        for i in playList:
            imageUrl = self._baseUrl + i[1] + "|Cookie=" + self._cookie_string + "&User-Agent=" + self._user_agent
            listitem = xbmcgui.ListItem(i[2],thumbnailImage=imageUrl)
            url = self.gen_plugin_url({"act": "detail", 
                                     "url": i[0],
                                     "title": i[2]})
            xbmcplugin.addDirectoryItem(self._handle, url, listitem, True)
        xbmcplugin.endOfDirectory(self._handle)
        
    def movie(self):
        self.getMovieList('/?m=vod-type-id-1.html')
    
    def tv(self):
        self.getMovieList('/?m=vod-type-id-2.html')
    
    def search(self):
        if "keyword" not in self._params:
            kb = Keyboard('',u'Please input Movie or TV Shows name 请输入想要观看的电影或电视剧名称')
            kb.doModal()
            if not kb.isConfirmed(): return
            sstr = kb.getText()
            if not sstr: return
            self.add_search_history(sstr)
        else:
            sstr = self._params["keyword"]
        if not sstr: return
        inputMovieName=urllib.quote_plus(sstr)
        # try:
        #     urlSearch = 'http://www.dnvod.tv/Movie/Search.aspx?tags=a'
        #     req = urllib2.Request(urlSearch, self._header)
        #     searchResponse = self._opener.open(req)
        # except urllib2.HTTPError as e:
        #     error_message=e.read()
        # #	print error_message
        #     detailReg = r'f\, (.*)={\"(.*)\":(.*)\};'
        #     detailPattern = re.compile(detailReg)
        #     detailResult = detailPattern.findall(error_message)
        #     first=detailResult[0][0]+"={\""+detailResult[0][1]+"\":"+detailResult[0][2]+"};"
        #     varname1=detailResult[0][0]
        #     varname2=detailResult[0][1]
        #     detailReg = r'challenge\-form\'\)\;\s*(.*)a.value = (.*)'
        #     detailPattern = re.compile(detailReg)
        #     detailResult = detailPattern.findall(error_message)
        #     second=detailResult[0][0]+"s = parseInt("+varname1+"."+varname2+", 10) + 12; "
        #     jscode="var s,"+first+second
        #     result=js2py.eval_js(jscode)
        #     soup = BeautifulSoup(error_message,"html.parser")
        #     fparam=soup.find_all('input')[0]['value']
        #     sparam=soup.find_all('input')[1]['value']
        #     searchData= urllib.urlencode({
        #         'jschl_vc': fparam,
        #         'pass': sparam,
        #         'jschl_answer': result
        #         })
        #     searchUrl = 'http://www.dnvod.tv/cdn-cgi/l/chk_jschl?'+'jschl_vc='+str(fparam)+'&pass='+str(sparam)+'&jschl_answer='+str(result)
        #     try:
        #         print searchUrl
        #         headers['Referer']='http://www.dnvod.tv/Movie/Search.aspx?tags=a'
        #         req = urllib2.Request(searchUrl, headers=Searchheaders)
        #         time.sleep(5)
        #         sresult = opener.open(req)
        #         # print sresult.read()
        #         print sresult.info()
        #     except urllib2.HTTPError as e:
        #         print e.code
        #         print e.read()
        
        #headers['Referer']='http://www.dnvod.tv/'
        urlSearch = 'http://www.dnvod.tv/Movie/Search.aspx?tags='+inputMovieName
        searchRequest = urllib2.Request(urlSearch,None, self._header)
        searchResponse = self._opener.open(searchRequest)
        searchdataResponse = searchResponse.read()
        searchReg = r'<a href="(.*%3d)">'
        searchPattern = re.compile(searchReg)
        urls = searchPattern.findall(searchdataResponse)

        searchRegName = r'3d" title="(.*)">'
        searchPatternName = re.compile(searchRegName)
        searchResultName = searchPatternName.findall(searchdataResponse)
        
        listitem = xbmcgui.ListItem('[COLOR FFFF00FF]Search result 当前搜索: [/COLOR][COLOR FFFFFF00]('+sstr+') [/COLOR][COLOR FF00FFFF] Total 共计：'+str(len(urls))+'[/COLOR]【[COLOR FF00FF00]'+'Click here for new search 点此输入新搜索内容'+'[/COLOR]】')
        url= self.gen_plugin_url({"act": "search"})
        xbmcplugin.addDirectoryItem(self._handle, url, listitem, True)
        for i in range(len(searchResultName)):
            listitem = xbmcgui.ListItem(searchResultName[i])
            url=self.gen_plugin_url({"act": "detail", "title": searchResultName[i],
                                     "url": urls[i]})
            xbmcplugin.addDirectoryItem(self._handle, url, listitem, True)
            print str(i+1)+': '+searchResultName[i]+'\n'
        xbmcplugin.endOfDirectory(self._handle)

    def episodes(self):
        url = self._params['url']
        title = self._params['title']
        filmIdReg = r'id=(.*%3d)'
        filmIdPattern = re.compile(filmIdReg)
        filmIdResult = filmIdPattern.findall(url)

        playlistUrlData = 'id=' + filmIdResult[0] + '&isk=0&visible=0&cinema=1&taxis=0&action=GetPlayList'

        playlistUrl = "http://m2.dnvod.tv/api/video/detail?id=" + filmIdResult[0] +  "&ispath=false&cinema=1&device=desktop&player=CkPlayer&tech=HLS&region=AU&country=NZ&lang=none&v=1"

        headers = utils.custom_header("m2.dnvod.tv", "http", "http://www.dnvod.tv/Movie/Readyplay.aspx?id=jydSM%2fudfCo%3d")
        playlistRequest = urllib2.Request(playlistUrl, playlistUrlData ,headers) 
        playlistResult = urllib2.urlopen(playlistRequest).read()
        playlist = json.loads(playlistResult)['data']['info'][0]['GuestSeriesList']

        detailResult = [i['Key'] for i in playlist]

        listitem = xbmcgui.ListItem('[COLOR FFFF00FF]Current Select 当前选择: [/COLOR][COLOR FFFFFF00]('+title+') [/COLOR]')
        url=sys.argv[0]+sys.argv[2]
        xbmcplugin.addDirectoryItem(self._handle, url, listitem, False)
        listitem = xbmcgui.ListItem('[COLOR FF00FFFF]Total '+str(len(detailResult))+'Episodes, 共计：'+str(len(detailResult))+' 集[/COLOR]')
        xbmcplugin.addDirectoryItem(self._handle, url, listitem, False)
        for i in range(len(detailResult)):
            episodeTitle = title + '--第' +str(i+1)+'集'
            listitem = xbmcgui.ListItem(episodeTitle)
            listitem.setInfo("video", {"Title": episodeTitle})
            listitem.setProperty("IsPlayable","true")
            url = self.gen_plugin_url({"act": "play", "id": detailResult[i],
                                       "title": episodeTitle})
            xbmcplugin.addDirectoryItem(self._handle, url, listitem, False)
        xbmcplugin.endOfDirectory(self._handle)
        
    def play(self):
        title = self._params['title']
        id = self._params['id']
        urlSec = "http://m2.dnvod.tv/api/video/play?id=" + id + "&ispath=false&cinema=1&device=desktop&player=CkPlayer&tech=HLS&region=AU&country=NZ&lang=none&v=1"
        headers = utils.custom_header("m2.dnvod.tv", "http", "http://www.dnvod.tv/Movie/Readyplay.aspx?id=jydSM%2fudfCo%3d")
        requestSec = urllib2.Request(urlSec,None, headers)
        responseSec = urllib2.urlopen(requestSec)
        url_response = json.loads(responseSec.read())

        real_url = url_response['data']['info'][0]['FlvPathList'][-1]['Result']
        self.play_url(real_url, title)
    
    def play_url(self, url, title):
        print("now playing: ", title, url)
        #playlist = xbmc.PlayList(1)
        #playlist.clear()
        listitem=xbmcgui.ListItem(title, path=url)
        #playlist.add(url, listitem=listitem)
        #xbmc.Player().play(playlist)
        #xbmc.Player().play(url, listitem)
        xbmcplugin.setResolvedUrl(self._handle, succeeded=True, listitem=listitem)