# -*- coding: utf-8 -*-

import xbmcgui, xbmcplugin
from pydoc import locate

providers = {"olevod": "olevodProvider.OlevodProvider",
             #"dnvod": "dnvodProvider.DnvodProvider",
             "haiwaiyy": "haiwaiyyProvider.HaiwaiyyProvider",
             "newcyy": "newcyyProvider.NewcyyProvider",
             "jiqimao": "jiqimaoProvider.JiqimaoProvider",
             "newasiantv": "newasiantvProvider.NewasaintvProvider",
             "maplestage": "maplestageProvider.MaplestageProvider"}

def get_provider(provider_name):
    return locate(providers[provider_name])()
    #return providers[provider_name]()

def route(handle, plugin_url, params):
    if 'provider' in params:
        provider_name = params['provider']
        provider = get_provider(provider_name)
        provider.route(params.get("act", "index"))
    else:
        for key in providers.keys():
            listitem = xbmcgui.ListItem(key)
            url = plugin_url + "?provider=" + key
            xbmcplugin.addDirectoryItem(handle, url, listitem, True)
        xbmcplugin.endOfDirectory(handle)
             