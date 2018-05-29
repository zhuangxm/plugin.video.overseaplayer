# -*- coding: utf-8 -*-

from provider import *
import utils
import cfscrape
import xbmcplugin
import base64
from xbmc import Keyboard
import xbmc

class OlevodProvider(Provider):
    def __init__(self):
        Provider.__init__(self)
        self._header = utils.custom_header("www.olevod.com", "https", "https://www.olevod.com")
        self._baseUrl = "https://www.olevod.com"
        self._name = "olevod"
        if len(self._cookie_string) > 0:
            self._header['Cookie'] = self._cookie_string
        if len(self._user_agent) > 0:
            self._header['User-Agent'] = self._user_agent

    def route(self, act):
        {"index": self.index,
         "movie": self.movie,
         "tv": self.tv,
         "search": self.search,
         "detail": self.episodes,
         "play": self.play}[act]()
        
    def index(self):
        scraper = cfscrape.create_scraper()
        response = scraper.get(self._baseUrl)
        result = response.content
        cookie_string = scraper.cookie_string()
        user_agent = scraper.headers["User-Agent"]

        for item in ["movie", "tv", "search"]:
            listitem=xbmcgui.ListItem(item)
            isFolder=True
            url = self.gen_plugin_url({"act": item,
                                       "name": item,
                                       'Cookie': cookie_string,
                                       "User-Agent": user_agent})
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
            #url=sys.argv[0]+'?act=Detail&url='+base64.urlsafe_b64encode(i[0])+'&title='+base64.urlsafe_b64encode(i[2])+'&cookie='+cookie_string
            xbmcplugin.addDirectoryItem(self._handle, url, listitem, True)
        xbmcplugin.endOfDirectory(self._handle)
        
    def movie(self):
        self.getMovieList('/?m=vod-type-id-1.html')
    
    def tv(self):
        self.getMovieList('/?m=vod-type-id-2.html')
    
    def search(self):
        kb = Keyboard('', 'Please input Movie or TV Shows name 请输入想要观看的电影或电视剧名称')
        kb.doModal()
        if not kb.isConfirmed(): return
        sstr = kb.getText()
        if not sstr: return
        inputMovieName=urllib.quote_plus(sstr)
            
        urlSearch = self._baseUrl + '/index.php?m=vod-search'
        data = 'wd='+inputMovieName
        req = urllib2.Request(urlSearch, data, self._header)
        searchResponse = self._opener.open(req).read()
        
        searchReg = r'<h6 class="fl">.*?<a href="(.*?)".*?>(.*?)</a>'
        searchResult = utils.parse(searchResponse, searchReg)
        
        listitem = xbmcgui.ListItem('[COLOR FFFF00FF]Search result 当前搜索: [/COLOR][COLOR FFFFFF00]('+sstr+') [/COLOR][COLOR FF00FFFF] Total 共计：'+str(len(searchResult))+'[/COLOR]【[COLOR FF00FF00]'+'Click here for new search 点此输入新搜索内容'+'[/COLOR]】')
        xbmcplugin.addDirectoryItem(self._handle, self.gen_plugin_url({"act": "search"}), listitem, True)
        for i in searchResult:
            listitem = xbmcgui.ListItem(i[1])
            url = self.gen_plugin_url({"act": "detail",
                                     "url": i[0],
                                     "title": i[1]})
            #url=sys.argv[0]+'?act=Detail&url='+base64.urlsafe_b64encode(i[0])+'&title='+base64.urlsafe_b64encode(i[1])
            xbmcplugin.addDirectoryItem(self._handle, url, listitem, True)
        xbmcplugin.endOfDirectory(self._handle)

    def episodes(self):
        print self._params
        url = base64.urlsafe_b64decode(self._params['url'])
        title = base64.urlsafe_b64decode(self._params['title'])
        print url
        urlDetail = self._baseUrl + url
        print urlDetail
        req = urllib2.Request(urlDetail, None, self._header)
        response = self._opener.open(req).read()
        reg = r'<li><a href="(.*?)".*?>(.*?)</a>'
        pattern = re.compile(reg)
        result = pattern.findall(response)
        for i in range(len(result)):
            item = result[i]
            episodeTitle = title + " " + item[1]
            listitem = xbmcgui.ListItem(episodeTitle)
            listitem.setInfo("video", {"Title": episodeTitle})
            listitem.setProperty("IsPlayable","true")
            url = self.gen_plugin_url({"act": "play",
                                     "url": item[0],
                                     "title": episodeTitle})
            #url=sys.argv[0]+'?act=Play&url='+base64.urlsafe_b64encode(item[0])+'&title='+ base64.urlsafe_b64encode(episodeTitle)
            xbmcplugin.addDirectoryItem(self._handle, url, listitem, False)
        xbmcplugin.endOfDirectory(self._handle)
    
    def play_url(self, url, title):
        #playlist = xbmc.PlayList(1)
        #playlist.clear()
        listitem=xbmcgui.ListItem(title, path=url)
        #playlist.add(url, listitem=listitem)
        #xbmc.Player().play(playlist)
        #xbmc.Player().play(url, listitem)
        xbmcplugin.setResolvedUrl(self._handle, succeeded=True, listitem=listitem)
    
    def play(self):
        url = base64.urlsafe_b64decode(self._params['url'])
        title = base64.urlsafe_b64decode(self._params['title'])

        urlPlay = self._baseUrl + url
        req = urllib2.Request(urlPlay, None, self._header)
        response = self._opener.open(req).read()
        reg = r'var url=\'(.*?)\'.*?replace\(\'(.*?)\'.*?\'(.*?)\''
        pattern = re.compile(reg)
        result = pattern.findall(response)
        print result
        url = result[0][0].replace(result[0][1],result[0][2]) + "|Cookie=" + self._cookie_string + "&User-Agent=" + self._user_agent
        print url
        self.play_url(url, title)
