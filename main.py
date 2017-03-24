from resources.lib.globals import *

params=get_params()
media_id=None
name=None
mode=None

try:
    media_id=urllib.unquote_plus(params["id"])
except:
    pass
try:
    name=urllib.unquote_plus(params["name"])
except:
    pass
try:
    mode=int(params["mode"])
except:
    pass


if mode==None:                    
    #or url==None or len(url)<1
    mainMenu()
elif mode==100:
    listShows()      
elif mode==101:
    listMovies()  
elif mode==102:
    getStream(media_id)
elif mode==103:
    getEpisodes(media_id)
elif mode==999:
	deauthorize()

xbmcplugin.endOfDirectory(addon_handle)