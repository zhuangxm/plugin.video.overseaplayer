# -*- coding: utf-8 -*-

from provider import *
import utils
import cfscrape
import xbmcplugin
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
        
    def index(self):
        scraper = cfscrape.create_scraper()
        response = scraper.get(self._baseUrl)
        result = response.content
        cookie_string = scraper.cookie_string()
        user_agent = scraper.headers["User-Agent"]

        for item,value in {"movie": "movie", "tv":"tv", "search": "load_search"}.iteritems():
            listitem=xbmcgui.ListItem(item)
            isFolder=True
            url = self.gen_plugin_url({"act": value,
                                       "name": value,
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
            xbmcplugin.addDirectoryItem(self._handle, url, listitem, True)
        xbmcplugin.endOfDirectory(self._handle)
        
    def movie(self):
        self.getMovieList('/?m=vod-type-id-1.html')
    
    def tv(self):
        self.getMovieList('/?m=vod-type-id-2.html')
    
    def search(self):
        if "keyword" not in self._params:
            kb = Keyboard('', 'Please input Movie or TV Shows name 请输入想要观看的电影或电视剧名称')
            kb.doModal()
            if not kb.isConfirmed(): return
            sstr = kb.getText()
            if not sstr: return
            self.add_search_history(sstr)
        else:
            sstr = self._params["keyword"]
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
            xbmcplugin.addDirectoryItem(self._handle, url, listitem, True)
        xbmcplugin.endOfDirectory(self._handle)

    def episodes(self):
        print self._params
        url = self._params['url']
        title = self._params['title']
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
            xbmcplugin.addDirectoryItem(self._handle, url, listitem, False)
        xbmcplugin.endOfDirectory(self._handle)
    
    def play(self):
        url = self._params['url']
        title = self._params['title']

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
