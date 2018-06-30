# -*- coding: utf-8 -*-

from provider import *
import utils
import xbmcplugin
from xbmc import Keyboard
import xbmc

class JiqimaoProvider(Provider):
    def __init__(self):
        Provider.__init__(self)
        self._header = utils.custom_header("jiqimao.tv", "http", "http://jiqimao.tv/")
        self._baseUrl = "http://jiqimao.tv"
        self._name = "jiqimao"
        if len(self._cookie_string) > 0:
            self._header['Cookie'] = self._cookie_string
        if len(self._user_agent) > 0:
            self._header['User-Agent'] = self._user_agent
        
    def index(self):
        # scraper = cfscrape.create_scraper()
        # response = scraper.get(self._baseUrl)
        # result = response.content
        # cookie_string = scraper.cookie_string()
        # user_agent = scraper.headers["User-Agent"]

        for item,value in {"movie": "movie", "tv":"tv", "search": "load_search"}.iteritems():
            listitem=xbmcgui.ListItem(item)
            isFolder=True
            url = self.gen_plugin_url({"act": value,
                                       "name": value})
            xbmcplugin.addDirectoryItem(self._handle,url,listitem,isFolder)
        xbmcplugin.endOfDirectory(self._handle)
        
    def list(self):
        url = self._params['url']
        self.getMovieList(url)
           
    def getMovieList(self, url):
        print url
        urlReg = r'/cate/more/(\d*)\?current=(\d*)'
        url_result = re.compile(urlReg).findall(url)[0]
        type_id = url_result[0]
        pageno = url_result[1]
        print url_result
        
        next_pageno = str(int(pageno) + 1)
        
        url = self._baseUrl + url
        print("getMoveList url", url)
        #print self._header
        
        
        req = urllib2.Request(url, None, self._header)
        result = self._opener.open(req).read()
        #print result
        # <a onclick="_hmt.push(['_trackEvent', 'web_movie_more', 'web_movie_more_同步热播_click', 'web_movie_more_同步热播_click_如果,爱'])" target="_blank" href="http://jiqimao.tv/movie/show/b9ba2016000f0f33689cc344c048b7315d112cd5">
        # <div class="three-tv-img">
        # <img src="http://tupian.tupianzy.com/pic/upload/vod/2018-05-28/201805281527467394.jpg" alt="如果,爱" onerror="loadDefaultMid();"></div>
        # <p class="big">如果,爱</p>
        # </a>        
        reg = r'<a onclick=".*?" target="_blank" href="(.*?)">\s*?<div class="three-tv-img">\s*?<img src="(.*?)" alt="(.*?)" onerror=".*?"></div>.*?</a>'
        playList = utils.parse(result, reg)
        print("playlist:", playList)
        for i in playList:
            imageUrl = self.get_full_url(i[1]) 
            listitem = xbmcgui.ListItem(i[2],thumbnailImage=imageUrl)
            url = self.gen_plugin_url({"act": "detail", 
                                     "url": i[0],
                                     "title": i[2]})
            xbmcplugin.addDirectoryItem(self._handle, url, listitem, True)
        listitem = xbmcgui.ListItem("next page >> " + next_pageno,thumbnailImage=imageUrl)
        url = self.gen_plugin_url({"act": "list", 
                                 "url": self.page_url(type_id, next_pageno)})            
        xbmcplugin.addDirectoryItem(self._handle, url, listitem, True)
        xbmcplugin.endOfDirectory(self._handle)
        
    def page_url(self, id, pageno):
        return "/cate/more/" + str(id) + "?current=" + str(pageno)
        
    def movie(self):
        self.category([('电影推荐',113), ('最新上映',98), ('动作片',120), ('喜剧片',121), ('爱情片',122), ('科幻片',123), ('剧情片',125), ('战争片',126), ('恐怖片',124)])
    
    def tv(self):
        self.category([('同步热播',89), ('国产剧',29), ('欧美联盟',31), ('日韩剧场',93), ('港台剧场',83)])
    
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
            
        #http://jiqimao.tv/search/video/%E4%B8%89%E5%9B%BD    
        urlSearch = self._baseUrl + '/search/video/' + inputMovieName
        print urlSearch
        req = urllib2.Request(urlSearch, None, self._header)
        searchResponse = self._opener.open(req).read()
        #print searchResponse
        # <a href="http://jiqimao.tv/movie/show/b1ddfe43fe64adcac286546ade2d1e28a2313448" target="_blank">
        #     <div class="search-tv-box">
        #         <img class="search-tv-img" src="http://tupian.tupianzy.com/pic/upload/vod/2018-03-28/201803281522238464.jpg" alt="三国机密之潜龙在渊" onerror="loadDefaultMid();">
        #         <div class="search-tv-title">
        #             三国机密之潜龙在渊
        #         </div>
        #         <div class="search-tv-pa-type">
        #             电视剧
        #         </div>
        #         <div class="search-tv-pa-episode">
        #             共54集
        #         </div>
        #     </div>
        # </a>
        searchReg = r'<a href="([-a-zA-Z0-9@:%_\+.~#?&//=]*?)" target="_blank">\s*?<div class="search-tv-box">\s*?<img class="search-tv-img" src="(.*?)" alt="(.*?)".*?>'
        searchResult = utils.parse(searchResponse, searchReg)
        #print searchResult
        
        listitem = xbmcgui.ListItem('[COLOR FFFF00FF]Search result 当前搜索: [/COLOR][COLOR FFFFFF00]('+sstr+') [/COLOR][COLOR FF00FFFF] Total 共计：'+str(len(searchResult))+'[/COLOR]【[COLOR FF00FF00]'+'Click here for new search 点此输入新搜索内容'+'[/COLOR]】')
        xbmcplugin.addDirectoryItem(self._handle, self.gen_plugin_url({"act": "search"}), listitem, True)
        for item in searchResult:
            title = item[2]
            listitem = xbmcgui.ListItem(title, thumbnailImage=self.get_full_url(item[1]))
            url = self.gen_plugin_url({"act": "detail",
                                     "url": item[0],
                                     "title": title})
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
        #<li><a title="" onclick="_hmt.push(['_trackEvent', 'web_player', 'web_player_click', 'web_player_click_如果,爱_1'])" target="_blank" href="http://jiqimao.tv/video/ckPlayer/604fb56dc909801639d01abebb60dcaa1823d7c2">1</a></li>
        #<a onclick="_hmt.push(['_trackEvent', 'web_player', 'web_player_click', 'web_player_click_死侍2_TC中字版'])" target="_blank" href="http://jiqimao.tv/video/ckPlayer/239cf7cbc0da03f54c18f5d6eb8e6415b7e338ca">TC中字版</a>
        reg = '<a.*?onclick="_hmt.*?" target=".*?" href="(.*?)">(.*?)</a>'
        pattern = re.compile(reg)
        result = pattern.findall(response)
        for i in range(len(result)):
            item = result[i]
            episodeTitle = title + " -- " + item[1]
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

        #"vod-play-id-17700-src-3-num-4.html"
        # urlReg = r'vod-play-id-\d*-src-(\d*)-num-(\d*).html'
        # url_result = re.compile(urlReg).findall(url)[0]
        # host_src = url_result[0]
        # ep_num = url_result[1]
        # print(host_src, ep_num)

        urlPlay = self.get_full_url(url)
        print("url to play: ", urlPlay)
        req = urllib2.Request(urlPlay, None, self._header)
        response = self._opener.open(req).read()
        #print response
        reg = r"var mode = '(.*?)';\s*?var sid = '(.*?)';\s*?var type = '(.*?)'"
        
        pattern = re.compile(reg)
        result = pattern.findall(response)[0]
        sid = result[1]
        mode = result[0]
        type = result[2]
        header = utils.custom_header("apick.jiqimao.tv", "http", urlPlay)
        req = urllib2.Request("http://apick.jiqimao.tv/service/ckplayer/parser?sid=" + sid + "&mode=iPad&type=1", None, header)
        response = json.loads(self._opener.open(req).read())
        movie_url = response['url']
        print("movie_url: ", movie_url)
        self.play_url(movie_url, title)
