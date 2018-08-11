# -*- coding: utf-8 -*-

from provider import *
import utils
import xbmcplugin
from xbmc import Keyboard
import xbmc
import dailymotion
import datetime

class MaplestageProvider(Provider):
    def __init__(self):
        Provider.__init__(self)
        self._header = utils.custom_header("maplestage.com", "http", "http://maplestage.com/")
        self._baseUrl = "http://maplestage.com"
        self._name = "maplestage"
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

        for item,value in {"tv":"tv", "search": "load_search"}.iteritems():
            listitem=xbmcgui.ListItem(item)
            isFolder=True
            url = self.gen_plugin_url({"act": value,
                                       "name": value})
            xbmcplugin.addDirectoryItem(self._handle,url,listitem,isFolder)
        xbmcplugin.endOfDirectory(self._handle)
        print("maple 5")
        # listitem = xbmcgui.ListItem("play")
        # listitem.setInfo("video", {"Title": "shaolin"})
        # listitem.setProperty("IsPlayable","true")
        # url = self.gen_plugin_url({"act": "play",
        #                            "id": "k1JY1GKNfwRtEnnTsod",
        #                            "title": "shaolin"})
        # xbmcplugin.addDirectoryItem(self._handle, url, listitem, False)
        # xbmcplugin.endOfDirectory(self._handle)
        
        
    def drama_list(self, type, year):
        req = urllib2.Request(self._baseUrl + "/drama/cn", None, self._header)
        response = self._opener.open(req).read()
        #print response
        reg = r'var pageProps =(.*?);'
        videos = utils.parse(response, reg)[0]
        #print videos
        videos = json.loads(videos)[type]
        for video in videos:
            imageUrl = self.get_full_url(video["cover"].encode("utf-8")) 
            title = video["name"].encode("utf-8")
            movie_year = video["year"]
            print (year, movie_year, title)
            if year == 0 or movie_year == year:
                print "add", title
                listitem = xbmcgui.ListItem(video["name"],thumbnailImage=imageUrl)
                movie_url = self._baseUrl + "/show/" + urllib.quote(video["slug"].encode("utf-8"))
                url = self.gen_plugin_url({"act": "detail", 
                                         "url": movie_url,
                                         "title": title})
                xbmcplugin.addDirectoryItem(self._handle, url, listitem, True)
        xbmcplugin.endOfDirectory(self._handle)

    def list(self):
        type = self._params['type']
        year = int(self._params['year'])
        self.drama_list(type , year)
        
    def category(self, cates):
        for item in cates:
            listitem = xbmcgui.ListItem(item[0])
            url = self.gen_plugin_url({"act": "list",
                                       "type": item[1],
                                       "year": item[2]})
            xbmcplugin.addDirectoryItem(self._handle, url, listitem, True)
        xbmcplugin.endOfDirectory(self._handle)
           
    def tv(self):
        year = datetime.date.today().year
        list = [('同步热播','hotShows',0)]
        for i in range(5):
            year_i = year - i
            list.append((str(year_i), 'shows', year_i))
        self.category(list)
    
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
        urlSearch = self._baseUrl + '/v1/search?q=' + inputMovieName
        print urlSearch
        req = urllib2.Request(urlSearch, None, self._header)
        searchResponse = self._opener.open(req).read()
        
        print searchResponse
        movie_list = json.loads(searchResponse)
        print movie_list
        
        #print searchResult
        
        listitem = xbmcgui.ListItem('[COLOR FFFF00FF]Search result 当前搜索: [/COLOR][COLOR FFFFFF00]('+sstr+') [/COLOR][COLOR FF00FFFF] Total 共计：'+str(len(movie_list))+'[/COLOR]【[COLOR FF00FF00]'+'Click here for new search 点此输入新搜索内容'+'[/COLOR]】')
        xbmcplugin.addDirectoryItem(self._handle, self.gen_plugin_url({"act": "search"}), listitem, True)
        for item in movie_list:
            title = item["name"].encode("utf-8")
            movie_url = self._baseUrl + "/show/" + urllib.quote(item["slug"].encode("utf-8"))
            print(title, movie_url)
            listitem = xbmcgui.ListItem(title, thumbnailImage=self.get_full_url(item["thumb"]))
            url = self.gen_plugin_url({"act": "detail",
                                       "url": movie_url,
                                       "title": title})
            xbmcplugin.addDirectoryItem(self._handle, url, listitem, True)
        xbmcplugin.endOfDirectory(self._handle)

    def episodes(self):
        print self._params
        url = self._params['url']
        title = self._params['title']
        urlDetail = self.get_full_url(url)
        print urlDetail
        req = urllib2.Request(urlDetail, None, self._header)
        response = self._opener.open(req).read()
        #print response
        reg = r'var pageData = .*?"episodes":\[(.*?)\].*?var'
        result = utils.parse(response, reg)[0]
        #print result
        episodes = json.loads("["+result+"]")
        #print episodes
        for episode in episodes:
            slug = episode["slug"].encode("utf-8")
            episodeTitle = slug + "--" + episode["numStr"].encode("utf-8") + " "
            if "topic" in episode:
                episodeTitle += episode["topic"].encode("utf-8")
            short_id = episode["shortId"].encode("utf-8")
            listitem = xbmcgui.ListItem(episodeTitle, thumbnailImage=episode['thumb'])
            listitem.setInfo("video", {"Title": episodeTitle})
            listitem.setProperty("IsPlayable","true")
            url = self.gen_plugin_url({"act": "play",
                                       "url": self.get_full_url("/episode/" + short_id + "/" + urllib.quote_plus(slug)),
                                       "title": episodeTitle})
            xbmcplugin.addDirectoryItem(self._handle, url, listitem, False)
        xbmcplugin.endOfDirectory(self._handle)
        
    # def get_video_id(self, url):
    #     req = urllib2.Request(url, None, self._header)
    #     response = self._opener.open(req).read()
    #     #print response
    #     reg = r'var pageData = .*?"name":"dailymotion","videos":\[(.*?)\].*?var'
    #     videos = utils.parse(response, reg)[0]
    #     print videos
    #     videos = json.loads("["+videos+"]")
    #     print videos
    #     for video in videos:
    #         video_type = video["type"].encode("utf-8")
    #         if video_type == "dailymotion":
    #             return video["id"].encode("utf-8")
                
    def parse_videos(self, page_data):
        props = page_data["props"]
        models = [i for i in props if i["name"] == "model"][0]["value"]["videoSources"]
        print("models",models)
        dailymotions = [i for i in models if i["name"] == "dailymotion" and not i["hidden"]]
        print("dailymotions", dailymotions)
        videos = dailymotions[0]["videos"]
        return videos
          
    def get_video_id(self,url):
        req = urllib2.Request(url, None, self._header)
        response = self._opener.open(req).read()
        #print response
        reg = r'var pageData = (.*?);'
        page_data = json.loads(utils.parse(response, reg)[0])
        print page_data
        videos = self.parse_videos(page_data)
        print("videos", videos)
        return videos[0]["id"].encode("utf-8")
        # videos = json.loads("["+videos+"]")
        # print videos
        # for video in videos:
        #     video_type = video["type"].encode("utf-8")
        #     if video_type == "dailymotion":
        #         return video["id"].encode("utf-8")
    
    def play(self):
        url = self._params["url"]
        title = self._params['title']
        print url
        print title
        video_id = self.get_video_id(url)
        print("video_id:",video_id)
        movie_url = dailymotion.getStreamUrl(video_id, False) 
        #movie_url = urllib.quote(movie_url, safe=":#&=/")
        print("movie_url", movie_url)        
        self.play_url(movie_url, title)

