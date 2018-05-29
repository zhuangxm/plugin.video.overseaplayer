# -*- coding: utf-8 -*-

import xbmcgui, xbmcplugin
from olevodProvider import OlevodProvider
from dnvodProvider import DnvodProvider

providers = {"olevod": OlevodProvider,
             "dnvod": DnvodProvider} 

def get_provider(provider_name):
    return providers[provider_name]()

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
             