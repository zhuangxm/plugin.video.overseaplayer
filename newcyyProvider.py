# -*- coding: utf-8 -*-

from provider import *
import utils
import cfscrape
import xbmcplugin
from xbmc import Keyboard
import xbmc

class NewcyyProvider(Provider):
    def __init__(self):
        Provider.__init__(self)
        self._header = utils.custom_header("www.newcyy.com", "https", "https://www.newcyy.com/")
        self._baseUrl = "https://www.newcyy.com"
        self._name = "newcyy"
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
        
    def page_url(self, id, pageno):
        return "/list/?" + str(id) + "-" + str(pageno) + ".html"
           
    def getMovieList(self, url):
        print url
        #/list/?1-1.html
        urlReg = r'/list/\?(\d*)-(\d*)\.html'
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
        #reg = r'<a href="([-a-zA-Z0-9@:%_\+.~#?&//=]*?)" class=".*?">\n<img.*?data-original="(.*?)".*?alt="(.*?)".*?/>'
        #<li class="i_list list_n2"><a href="/detail/?9551.html" target="_blank"><img class="waitpic" src="/public/image/thumb_2.png" data-original="/uploads/allimg/180406/3754f8a2fb30c12e.jpg" alt="猛龙怪客" width="405" height="555"></a>
        reg = r'<li class="i_list list_n2"><a href="(.*?)" target="_blank"><img class="waitpic" src=".*?" data-original="(.*?)" alt="(.*?)".*?></a>'
        playList = utils.parse(result, reg)
        print("playlist:", playList)
        for i in playList:
            title = i[2]
            imageUrl = i[1]
            if not imageUrl.startswith("http"):
                imageUrl = self._baseUrl + imageUrl
            #print imageUrl
            listitem = xbmcgui.ListItem(title,thumbnailImage=imageUrl)
            url = self.gen_plugin_url({"act": "detail", 
                                     "url": i[0],
                                     "title": title})
            xbmcplugin.addDirectoryItem(self._handle, url, listitem, True)
        listitem = xbmcgui.ListItem("next page >> " + next_pageno,thumbnailImage=imageUrl)
        url = self.gen_plugin_url({"act": "list", 
                                 "url": self.page_url(type_id, next_pageno)})            
        xbmcplugin.addDirectoryItem(self._handle, url, listitem, True)
        xbmcplugin.endOfDirectory(self._handle)

    def movie(self):
        self.category([('全部电影',1), ('动作片',5), ('喜剧片',10), ('爱情片',6), ('科幻片',7), ('记录片',11), ('伦理片',37), ('剧情片',12), ('战争片',9), ('恐怖片',8)])
    
    def tv(self):
        self.category([('全部电视剧',2), ('国产剧',13), ('欧美联盟',15), ('日韩剧场',16), ('港台剧场',14), ('海外剧场',17)])
        
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
        #https://www.newcyy.com/search.php?searchword=
        urlSearch = self._baseUrl + '/search.php?searchword='+inputMovieName
        print urlSearch
        req = urllib2.Request(urlSearch, None, self._header)
        searchResponse = self._opener.open(req).read()
        #print searchResponse
        reg = r'<li class="i_list list_n2"><a href="(.*?)" target="_blank"><img class="waitpic" src=".*?" data-original="(.*?)" alt="(.*?)".*?></a>'
        searchResult = utils.parse(searchResponse, reg)
        
        listitem = xbmcgui.ListItem('[COLOR FFFF00FF]Search result 当前搜索: [/COLOR][COLOR FFFFFF00]('+sstr+') [/COLOR][COLOR FF00FFFF] Total 共计：'+str(len(searchResult))+'[/COLOR]【[COLOR FF00FF00]'+'Click here for new search 点此输入新搜索内容'+'[/COLOR]】')
        xbmcplugin.addDirectoryItem(self._handle, self.gen_plugin_url({"act": "search"}), listitem, True)
        for item in searchResult:
            title = item[2]
            imageUrl = item[1]
            if not imageUrl.startswith("http"):
                imageUrl = self._baseUrl + imageUrl

            listitem = xbmcgui.ListItem(title, thumbnailImage=imageUrl)
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
        urlDetail = self._baseUrl + url
        print urlDetail
        req = urllib2.Request(urlDetail, None, self._header)
        response = self._opener.open(req).read()
        #print response
        #<li><a title='HD高清' href='/video/?12921-0-0.html' target="_self">HD高清</a></li>
        reg = r"""<li><a title='(.*?)' href='(.*?)' target="_self">.*?</a></li>"""
        pattern = re.compile(reg)
        result = pattern.findall(response)
        for i in range(len(result)):
            item = result[i]
            episodeTitle = title + " " + item[0]
            url = item[1]
            host_src, ep_num = self.parse_video_html(url)
            listitem = xbmcgui.ListItem(episodeTitle)
            listitem.setInfo("video", {"Title": episodeTitle})
            listitem.setProperty("IsPlayable","true")
            url = self.gen_plugin_url({"act": "play",
                                     "url": url,
                                     "title": episodeTitle})
            xbmcplugin.addDirectoryItem(self._handle, url, listitem, False)
        xbmcplugin.endOfDirectory(self._handle)
    
    def parse_video_html(self, url):
        #video/?9551-0-0.html
        urlReg = r'\?\d*-(\d*)-(\d*).html'
        url_result = re.compile(urlReg).findall(url)[0]
        host_src = url_result[0]
        ep_num = url_result[1]
        return host_src, ep_num
    
    def play(self):
        url = self._params['url']
        title = self._params['title']
        host_src,ep_num = self.parse_video_html(url)
        print(host_src, ep_num)

        urlPlay = self._baseUrl + url
        print("url to play: ", urlPlay)
        req = urllib2.Request(urlPlay, None, self._header)
        response = self._opener.open(req).read()
        #print response
        #VideoInfoList="ckm3u8$$HD高清$https://youku.cdn-tudou.com/20180525/6123_836f65fc/index.m3u8$ckm3u8$$$kuyun$$HD高清$https://youku.cdn-tudou.com/share/4ca82b2a861f70cd15d83085b000dbde$kuyun"
        reg = r'VideoInfoList="(.*?)"'
        pattern = re.compile(reg)
        result = pattern.findall(response)[0]
        sites = result.split("$$$")
        #print sites
        for i in range(len(sites)):
            site_remove_title = sites[i].split("$$")[1]
            movie = site_remove_title.split("#")[int(ep_num)]
            movie_info = movie.split("$")
            sites[i] = movie_info[1]
        
        movie_url = sites[int(host_src)]
        if "m3u8" not in movie_url: 
            for movie in sites:
                if "m3u8" in movie:
                    movie_url = movie
                    break
        print(ep_num, movie_url)
        # url = result[0][0].replace(result[0][1],result[0][2]) + "|Cookie=" + self._cookie_string + "&User-Agent=" + self._user_agent
        # print url
        self.play_url(movie_url, title)
