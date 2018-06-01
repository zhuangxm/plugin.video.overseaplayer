# -*- coding: utf-8 -*-

## using zip -r -0 oversea.zip plugin.video.overseaplayer/ to zip

import urlparse,xbmcaddon
import dispatcher

addon = xbmcaddon.Addon(id='plugin.video.overseaplayer')
__language__ = addon.getLocalizedString
plugin_url = sys.argv[0]
handle = int(sys.argv[1])
params = dict(urlparse.parse_qsl(sys.argv[2].lstrip('?')))

dispatcher.route(handle, plugin_url, params)