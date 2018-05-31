# -*- coding: utf-8 -*-

from provider import *
import utils
import cfscrape
import xbmcplugin
from xbmc import Keyboard
import xbmc
import js2py

class NewasaintvProvider(Provider):
    def __init__(self):
        Provider.__init__(self)
        self._header = utils.custom_header("www1.newasiantv.co", "http", "http://www1.newasiantv.co")
        self._baseUrl = "http://www1.newasiantv.co"
        self._name = "newasiantv"
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

        for item,value in {"tv":"tv", "movie": "movie"}.items():
            listitem=xbmcgui.ListItem(item)
            isFolder=True
            url = self.gen_plugin_url({"act": value,
                                       "name": value,
                                       'Cookie': cookie_string,
                                       "User-Agent": user_agent})
            xbmcplugin.addDirectoryItem(self._handle,url,listitem,isFolder)
        xbmcplugin.endOfDirectory(self._handle)
        
    def drama_url(self, country_id, pageno):
        return "/drama/" + str(pageno) + "&country_id=" + str(country_id)
    
    def movie_url(self, pageno):
        return "/movie/" + str(pageno)
        
    def pageno_url(self, url, pageno):
        return self.get_full_url(url).replace("$pageno$", str(pageno))
        
    def list(self):
        url = self._params['url']
        pageno = self._params['pageno']
        self.getMovieList(url, pageno)
        
    def getMovieList(self, page_url, pageno):
        url = self.pageno_url(page_url, pageno)
        next_pageno = str(int(pageno) + 1)
        print("getMoveList url", url)
        req = urllib2.Request(url, None, self._header)
        result = self._opener.open(req).read()
        #print result
        reg = r'<div class="img">\s*?<a href="(.*?)" title="(.*?)"><img src="(.*?)"/>.*?</a>\s*?</div>'
        playList = utils.parse(result, reg)
        print("playlist:", playList)
        for i in playList:
            imageUrl = self.get_full_url(i[2]) + "|Cookie=" + self._cookie_string + "&User-Agent=" + self._user_agent
            listitem = xbmcgui.ListItem(i[1],thumbnailImage=imageUrl)
            url = self.gen_plugin_url({"act": "detail", 
                                     "url": i[0],
                                     "title": i[1]})
            xbmcplugin.addDirectoryItem(self._handle, url, listitem, True)
        listitem = xbmcgui.ListItem("next page >> " + next_pageno)
        url = self.gen_plugin_url({"act": "list",
                                   "url": page_url,
                                   "pageno": next_pageno})
        xbmcplugin.addDirectoryItem(self._handle, url, listitem, True)
        xbmcplugin.endOfDirectory(self._handle)
        
    def movie(self):
        self.getMovieList('/movie/$pageno$',1)
    
    def tv(self):
        self.getMovieList('/drama/$pageno$&country_id=2', 1)
    
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
        urlDetail = self.get_full_url(url)
        print urlDetail
        req = urllib2.Request(urlDetail, None, self._header)
        response = self._opener.open(req).read()
        #print response
        reg = r'<a class="watch_button now" href="(.*?)">WATCH NOW</a>'
        pattern = re.compile(reg)
        real_page_url = pattern.findall(response)[0]

        req = urllib2.Request(real_page_url, None, self._header)
        response = self._opener.open(req).read()
        
        #print response
        reg = r'<a id="\d*?" href="(.*?)" episode-type="watch" title="(.*?)">.*?</a></li>'
        result = utils.parse(response, reg)
        
        for i in range(len(result)):
            item = result[i]
            episodeTitle = title + " " + item[1]
            print item[1]
            if 'V.I.P' in item[1]:
                continue
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

        urlPlay = self.get_full_url(url)
        print(urlPlay)
        req = urllib2.Request(urlPlay, None, self._header)
        response = self._opener.open(req).read()
        #print response
        reg = r'src="(http://[\w/\.]*?main.js.*?)"'
        main_js_url = utils.parse(response, reg)[0]
        
        main_js_host = urlparse.urlparse(main_js_url).netloc
        header = utils.custom_header(main_js_host, "http", urlPlay)
        header['Cookie'] = self._header['Cookie']
        header['User-Agent'] = self._header['User-Agent']
        print(main_js_url, header)
        request = urllib2.Request(main_js_url, None, header)
        main_js_str = self._opener.open(request).read()
        reg = r'var API_URL = \'(.*?)\';.*?var filmId="(\d*?)";\s*?var currentEp="(\d*?)".*?episodeJson =\s*?\'(.*?)\';'
        result = utils.parse(response,reg)[0]
        print result
        api_url = result[0]
        film_id = result[1]
        current_ep = int(result[2])
        episodes = json.loads(result[3])
        #print episodes
        episode = {}
        for item in episodes:
            if item['episodeId'] == current_ep:
                episode = item
                break
        print episode
        loader_url = api_url + "loader.php"
        header =  utils.custom_header("player.newasiantv.co", "http", urlPlay)
        data = {"url": episode["url"], "subUrl": episode["subUrl"],"eid": episode["episodeId"], "filmId": film_id}
        print(loader_url, data)
        request = urllib2.Request(loader_url, urllib.urlencode(data), header)
        response = self._opener.open(request).read()
        print response
        
        reg = r'file:(decodeLink.*?\))'
        result = utils.parse(response, reg)[0]
        print(result)
        #password = "1522609829" + result[1] + "replaceindexOfclick"
        password = "15226098292016replaceindexOfclick"
        print(len(password))
        #url_encrpyted = "U2FsdGVkX18/qUOTpktZKVoTKGDrP6Ekhpou4qpThDrWweC6WoA9oG/mnzshitfqDGwpieVLK6WWZ4P9WOWECub/nbThs8AolTvlZn2RPXpMlnbhZqc8tR4kAiUUognI6s+PkKes93pz7XhxQakxk227e6CP5mTWVLehFBnPxT+6/0QcUg9QOVSKTcatRXVtZ44DBSCZVR8GtsVT+seDWw=="
        
        js_str = main_js_str + "; " + result +";"
        print js_str
        # print len(url_encrpyted)
        # print aes.decrypt(url_encrpyted, password)
        #print js2py.eval_js(js_str)
        context = js2py.EvalJs()
        context.execute("""escape = function(text){pyimport urllib; return urllib.quote(text)};
        unescape = function(text){pyimport urllib; return urllib.unquote(text)};
        encodeURI = function(text){pyimport urllib; return urllib.quote(text, safe='~@#$&()*!+=:;,.?/\\'')};
        decodeURI = unescape;
        encodeURIComponent = function(text){pyimport urllib; return urllib.quote(text, safe='~()*!.\\'')};
        decodeURIComponent = unescape;""")
        movie_url = context.eval(js_str)
        #print aes.decrypt(result[0], password)
        # url = result[0][0].replace(result[0][1],result[0][2]) + "|Cookie=" + self._cookie_string + "&User-Agent=" + self._user_agent
        movie_url = urllib.quote(movie_url, safe=":/")
        print(movie_url, title)
        self.play_url(movie_url, title)
