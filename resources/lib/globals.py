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
BASE_URL = 'https://androidtv-api-us.crackle.com/Service.svc'
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
    url = f"/genres/{id}/all/US?format=json"
    json_source = json_request(url)
    for genre in json_source['Items']:
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
    url = f"/details/media/{id}/US?format=json"
    json_source = json_request(url)
    stream_url = ''
    stream_480_url = ''
    for stream in json_source['MediaURLs']:
        if 'Widevine_DASH' in stream['Type']:            
            stream_url = stream['DRMPath']
        if any(t in stream['Type'] for t in ['480p_1mbps.mp4', '480p.mp4']):
            stream_480_url = stream['Path']

    headers = 'User-Agent='+UA_WEB
    listitem = xbmcgui.ListItem()
    lic_url = f"https://license-wv.crackle.com/raw/license/widevine/{id}/us"
    license_key = f"{lic_url}|{headers}&Content-Type=application/octet-stream|R{{SSM}}|"
    if 'mpd' in stream_url:
        is_helper = inputstreamhelper.Helper('mpd', drm='widevine')
        if not is_helper.check_inputstream():
            sys.exit()
        listitem.setPath(stream_url)
        listitem.setProperty('inputstream', 'inputstream.adaptive')
        listitem.setProperty('inputstream.adaptive.manifest_type', 'mpd')
        listitem.setProperty('inputstream.adaptive.stream_headers', f"User-Agent={UA_WEB}")
        listitem.setProperty('inputstream.adaptive.license_type', 'com.widevine.alpha')
        listitem.setProperty('inputstream.adaptive.license_key', license_key)
        listitem.setMimeType('application/dash+xml')
        listitem.setContentLookup(False)
    else:
        stream_url = stream_480_url + "|" + headers
        listitem.setPath(stream_url)

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
        url = str(item['externalId'])
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
    url = BASE_URL + url
    xbmc.log(url)
    headers = {
        'Connection': 'keep-alive',
        'User-Agent': UA_ANDROID,
        'Authorization': get_auth(url),
        'X-Requested-With': 'com.crackle.androidtv'
    }

    r = requests.get(url, headers=headers, verify=False)

    return r.json()


def calc_hmac(src):
    # return hmac.new(base64.b64decode(PARTNER_KEY), src, hashlib.md5).hexdigest()
    return hmac.new(base64.b64decode(PARTNER_KEY), str(src).encode('utf-8'), hashlib.sha1).hexdigest()


def get_auth(url):
    timestamp = strftime('%Y%m%d%H%M', gmtime())
    # encoded_url = str(calc_hmac(url+"|"+timestamp)).upper() + "|" + timestamp + "|" + PARTNER_ID
    encoded_url = f"{calc_hmac(f'{url}|{timestamp}').upper()}|{timestamp}|{PARTNER_ID}|1"

    return encoded_url


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
