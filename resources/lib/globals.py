import sys, os, re
import urllib, requests
import base64, hmac, hashlib, inputstreamhelper
from time import gmtime, strftime
from kodi_six import xbmc, xbmcplugin, xbmcgui, xbmcaddon

if sys.version_info[0] > 2:
    urllib = urllib.parse

addon_url = sys.argv[0]
addon_handle = int(sys.argv[1])
ADDON = xbmcaddon.Addon()
ROOTDIR = ADDON.getAddonInfo('path')
FANART = os.path.join(ROOTDIR,"resources","media","fanart.jpg")
ICON = os.path.join(ROOTDIR,"resources","media","icon.png")


# Addon Settings
LOCAL_STRING = ADDON.getLocalizedString
UA_CRACKLE = 'Crackle/7.60 CFNetwork/808.3 Darwin/16.3.0'
UA_WEB = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36'
UA_ANDROID = 'Android 4.1.1; E270BSA; Crackle 4.4.5.0'
PARTNER_KEY = 'Vk5aUUdYV0ZIVFBNR1ZWVg=='
PARTNER_ID = '77'
#BASE_URL = 'https://androidtv-api-us.crackle.com/Service.svc'
BASE_URL = 'https://prod-api.crackle.com'
# found in https://prod-api.crackle.com/appconfig (platformId)
WEB_KEY = '5FE67CCA-069A-42C6-A20F-4B47A8054D46'



def main_menu():
    add_dir(LOCAL_STRING(30001), 'movies', 99, ICON)
    add_dir(LOCAL_STRING(30002), 'shows', 99, ICON)
    add_dir(LOCAL_STRING(30003), 'search', 104, ICON)

def list_movies(genre_id):
    url = f"/browse/movies/full/{genre_id}/alpha-asc/US?format=json"
    json_source = json_request(url)    
    
    for movie in json_source['Entries']:
        title = movie['Title']
        url = str(movie['ID'])
        icon = movie['ChannelArtTileLarge']
        fanart = movie['Images']['Img_1920x1080']
        info = {'plot':movie['Description'],
                'genre':movie['Genre'],
                'year':movie['ReleaseYear'],
                'mpaa':movie['Rating'],
                'title':title,
                'originaltitle':title,
                'duration':movie['DurationInSeconds'],
                'mediatype': 'movie'
                }

        add_stream(title,url,'movies',icon,fanart,info)

    xbmcplugin.addSortMethod(addon_handle, xbmcplugin.SORT_METHOD_LABEL)
    xbmcplugin.addSortMethod(addon_handle, xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE)


def list_genre(id):
    #url = f"/genres/{id}/all/US?format=json"    
    #url = f'/browse/{id}?enforcemediaRights=true&sortOrder=latest&pageNumber=1&pageSize=45'
    url = 'https://prod-api.crackle.com/browse/movies?genreType=Action&enforcemediaRights=true&sortOrder=latest&pageNumber=1&pageSize=45'
    json_source = json_request(url)
    for genre in json_source['data']['items']:
        title = genre['Name']

        add_dir(title, id, 100, ICON, genre_id=genre['ID'])
        # add_dir(name, id, mode, icon, fanart=None, info=None, genre_id=None)

    xbmcplugin.addSortMethod(addon_handle, xbmcplugin.SORT_METHOD_LABEL)
    xbmcplugin.addSortMethod(addon_handle, xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE)


def list_shows(genre_id):
    url = f"/browse/shows/full/{genre_id}/alpha-asc/US/1000/1?format=json"
    json_source = json_request(url)

    for show in json_source['Entries']:
        title = show['Title']
        url = str(show['ID'])
        icon = show['ChannelArtTileLarge']
        fanart = show['Images']['Img_TTU_1280x720']
        if fanart == "":
            fanart = show['Images']['Img_1920x1080']
        info = {'plot':show['Description'],
                'genre':show['Genre'],
                'year':show['ReleaseYear'],
                'mpaa':show['Rating'],
                'title':title,
                'originaltitle':title,
                'duration':show['DurationInSeconds'],
                'mediatype': 'tvshow'
                }

        add_dir(title,url,102,icon,fanart,info,content_type='tvshows')

    xbmcplugin.addSortMethod(addon_handle, xbmcplugin.SORT_METHOD_LABEL)
    xbmcplugin.addSortMethod(addon_handle, xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE)


def get_episodes(channel):
    url = f"/channel/{channel}/playlists/all/US?format=json"
    json_source = json_request(url)

    for episode in json_source['Playlists'][0]['Items']:
        episode = episode['MediaInfo']
        title = episode['Title']
        id = str(episode['Id'])
        icon = episode['Images']['Img_460x460']
        fanart = episode['Images']['Img_1920x1080']
        info = {'plot':episode['Description'],
                #'genre':episode['Genre'],
                'year':episode['ReleaseYear'],
                'mpaa':episode['Rating'],
                'tvshowtitle':episode['ShowName'],
                'title':title,
                'originaltitle':title,
                'duration':episode['Duration'],
                'season':episode['Season'],
                'episode':episode['Episode'],
                'mediatype': 'episode'
                }

        add_stream(title,id,'tvshows',icon,fanart,info)

    xbmcplugin.addSortMethod(addon_handle, xbmcplugin.SORT_METHOD_EPISODE)


def get_movie_id(channel):
    url = f"/channel/{channel}/playlists/all/US?format=json"
    json_source = json_request(url)

    return str(json_source['Playlists'][0]['Items'][0]['MediaInfo']['Id'])


def get_stream(id):
    #url = f"/details/media/{id}/US?format=json"
    id = "8f249799-3599-4bbf-afb3-4f6401b9059d"
    url = f'/playback/vod/{id}'
    json_source = json_request(url)
    stream_url = ''    
    for stream in json_source['data']['streams']:
        if 'widevine' in stream['type']:            
            stream_url = stream['url']
            lic_url = stream['drm']['keyUrl']
        
    headers = 'User-Agent='+UA_WEB
    listitem = xbmcgui.ListItem()
    #lic_url = f"https://license-wv.crackle.com/raw/license/widevine/{id}/us"
    #lic_url = "https://widevine-license.crackle.com"
    #license_key = f"{lic_url}|{headers}&Content-Type=application/octet-stream&Origin=https://www.crackle.com|R{{SSM}}|"
    if 'mpd' in stream_url:
        stream_url = get_stream_session(stream_url)
        is_helper = inputstreamhelper.Helper('mpd', drm='widevine')
        if not is_helper.check_inputstream():
            sys.exit()
    
        listitem.setPath(stream_url)
        listitem.setMimeType('application/dash+xml')
        listitem.setContentLookup(False)

        listitem.setProperty('inputstream', 'inputstream.adaptive')
        #listitem.setProperty('inputstream.adaptive.manifest_type', 'mpd') # Deprecated on Kodi 21
        listitem.setProperty('inputstream.adaptive.license_type', 'com.widevine.alpha')

        license_headers = {
            'User-Agent': UA_WEB,
            'Content-Type': 'application/octet-stream',
            'Origin': 'https://www.crackle.com'
        }
        from urllib.parse import urlencode
        license_config = { # for Python < v3.7 you should use OrderedDict to keep order
            'license_server_url': lic_url,
            'headers': urlencode(license_headers),
            'post_data': 'R{SSM}',
            'response_data': 'R'
        }
        listitem.setProperty('inputstream.adaptive.license_key', '|'.join(license_config.values()))
    else:
        # Return Error message
        sys.exit()

    xbmcplugin.setResolvedUrl(addon_handle, True, listitem)

def search(search_phrase):
    url = f"https://prod-api.crackle.com/contentdiscovery/search/{search_phrase}" \
          "?useFuzzyMatching=false" \
          "&enforcemediaRights=true" \
          "&pageNumber=1&pageSize=20" \
          "&contentType=Channels" \
          "&searchFields=Title%2CCast"
    headers = {
        'User-Agent': UA_WEB,
        'X-Crackle-Platform': WEB_KEY,
    }

    r = requests.get(url, headers=headers)
    xbmc.log(r.text)
    for item in r.json()['data']['items']:        
        metadata = item['metadata'][0]
        title = metadata['title']
        #url = str(item['externalId'])
        url = item['id']
        icon = get_image(item['assets']['images'], 220, 330)
        fanart = get_image(item['assets']['images'], 1920, 1080)
        info = {'plot': metadata['longDescription'],
                'title':title,
                'originaltitle':title,
                }

        if item['type'] == 'Movie':
            add_stream(title,url,'movies',icon,fanart,info)
        else:
            add_dir(title, url, 102, icon, fanart, info, content_type='tvshows')

def get_image(images, width, height):
    img = ICON
    for image in images:
        if image['width'] == width and image['height'] == height:
            img = image['url']
            break

    return img


def json_request(url):
    url = f'{BASE_URL}{url}'
    xbmc.log(url)
    headers = {
        'User-Agent': UA_WEB,
        'X-Crackle-Platform': WEB_KEY,
    }

    r = requests.get(url, headers=headers, verify=False)
    xbmc.log(r.text)
    return r.json()

def get_stream_session(url):
    #https://prod-vod-cdn1.crackle.com/v1/session/ab95b45b71c711ddf59f86e4e6bea571f56e1289/v2mt-prod-crackle-cloudfront/fef95e6b5ee695e858b64691c95f580f/us-west-2/out/v1/a9bb5767d92d45b5bc71f526ff968a27/cc1a04f1519a4e01acf1471c93fb6e40/84df441594d74061995f0a3fd170d3e5/index.mpd
    xbmc.log(f"Get Session from stream:{url}")     
    headers = {
        'User-Agent': UA_WEB,
    }

    r = requests.post(url, headers=headers, json={}, verify=False)
    xbmc.log(r.text)
    return f"https://prod-vod-cdn1.crackle.com{r.json()['manifestUrl']}"


def add_stream(name, id, stream_type, icon, fanart, info=None):
    ok = True
    u=addon_url+"?id="+urllib.quote_plus(id)+"&mode="+str(103)+"&type="+urllib.quote_plus(stream_type)
    listitem=xbmcgui.ListItem(name)
    if fanart is None: fanart = FANART
    listitem.setArt({'icon': icon, 'thumb': icon, 'poster': icon, 'fanart': fanart})
    listitem.setProperty("IsPlayable", "true")
    if info is not None:
        listitem.setInfo( type="video", infoLabels=info)
    ok = xbmcplugin.addDirectoryItem(handle=addon_handle,url=u,listitem=listitem,isFolder=False)
    xbmcplugin.setContent(addon_handle, stream_type)
    return ok


def add_dir(name, id, mode, icon, fanart=None, info=None, genre_id=None, content_type='videos'):
    ok = True
    u = addon_url+"?id="+urllib.quote_plus(id)+"&mode="+str(mode)
    if genre_id is not None: u += f"&genre_id={genre_id}"
    listitem=xbmcgui.ListItem(name)
    if fanart is None: fanart = FANART
    listitem.setArt({'icon': icon, 'thumb': icon, 'poster': icon, 'fanart': fanart})
    if info is not None:
        listitem.setInfo( type="video", infoLabels=info)
    ok = xbmcplugin.addDirectoryItem(handle=addon_handle,url=u,listitem=listitem,isFolder=True)
    xbmcplugin.setContent(addon_handle, content_type)
    return ok


def get_params():
    param=[]
    paramstring=sys.argv[2]
    if len(paramstring)>=2:
            params=sys.argv[2]
            cleanedparams=params.replace('?','')
            if (params[len(params)-1]=='/'):
                    params=params[0:len(params)-2]
            pairsofparams=cleanedparams.split('&')
            param={}
            for i in range(len(pairsofparams)):
                    splitparams={}
                    splitparams=pairsofparams[i].split('=')
                    if (len(splitparams))==2:
                            param[splitparams[0]]=splitparams[1]

    return param
