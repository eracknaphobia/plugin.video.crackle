import sys, os
import xbmc, xbmcplugin, xbmcgui, xbmcaddon
import urllib, urllib2
import json
import base64



addon_handle = int(sys.argv[1])
ADDON = xbmcaddon.Addon(id='plugin.video.crackle')
ROOTDIR = ADDON.getAddonInfo('path')
FANART = ROOTDIR+"/resources/media/fanart.jpg"
ICON = ROOTDIR+"/resources/media/icon.png"

#Addon Settings 
LOCAL_STRING = ADDON.getLocalizedString
UA_CRACKLE = 'Crackle/7.60 CFNetwork/808.3 Darwin/16.3.0'

def mainMenu():    
    addDir('Movies','/movies',101,ICON)
    addDir('TV','/tv',102,ICON)


def listMovies():       
    '''
    GET https://ios-api-us.crackle.com/Service.svc/browse/movies/full/all/alpha-asc/US?pageSize=24&pageNumber=1&format=json HTTP/1.1
    Host: ios-api-us.crackle.com
    Accept: */*
    Connection: keep-alive
    If-None-Match: "6a673366-2e5e-493e-98ae-28ead1f5b50e"
    Cookie: GR=348
    Accept-Language: en-us
    Authorization: 0C67DB845C62EB7437EF00F68376CE784A382046|201703231633|22|1
    Accept-Encoding: gzip, deflate
    User-Agent: Crackle/7.60 CFNetwork/808.3 Darwin/16.3.0
    '''
    url = 'http://ios-api-us.crackle.com/Service.svc/browse/movies/full/all/alpha-asc/US'
    url += '?pageSize=500'
    url += '&pageNumber=1'
    url += '&format=json'
    req = urllib2.Request(url)
    req.add_header("Connection", "keep-alive")
    req.add_header("Accept", "*/*")
    req.add_header("Accept-Encoding", "deflate")
    req.add_header("Accept-Language", "en-us")
    req.add_header("Connection", "keep-alive")    
    req.add_header("User-Agent", UA_CRACKLE)
    response = urllib2.urlopen(req)   
    json_source = json.load(response)                       
    response.close() 
    

    for movie in json_source['Entries']:        
        title = movie['Title']
        url = str(movie['ID'])
        icon = movie['ChannelArtTileLarge']
        fanart = movie['Images']['Img_1920x1080']
        info = None
        info = {'plot':movie['Description'],
                'genre':movie['Genre'], 
                'year':movie['ReleaseYear'], 
                'mpaa':movie['Rating'], 
                'title':title,
                'originaltitle':title,
                'duration':movie['DurationInSeconds']
                }

        addStream(title,url,'movies',icon,fanart,info)



def listEpisodes(season):    
    url = "http://fapi2.fxnetworks.com/androidtv/videos?filter%5Bfapi_show_id%5D=9aad7da1-093f-40f5-b371-fec4122f0d86&filter%5Bseason%5D="+season+"&limit=500&filter%5Btype%5D=episode"    
    req = urllib2.Request(url)
    req.add_header("Connection", "keep-alive")
    req.add_header("Accept", "*/*")
    req.add_header("Accept-Encoding", "deflate")
    req.add_header("Accept-Language", "en-us")
    req.add_header("Connection", "keep-alive")
    req.add_header("Authentication", "androidtv:a4y4o0e01jh27dsyrrgpvo6d1wvpravc2c4szpp4")
    req.add_header("User-Agent", UA_FX)
    response = urllib2.urlopen(req)   
    json_source = json.load(response)                       
    response.close() 
    
    for episode in reversed(json_source['videos']):            
        title = episode['name']
        #Default video type is 16x9
        url = episode['video_urls']['16x9']['en_US']['video_url']         
        try: url = episode['video_urls'][RATIO]['en_US']['video_url']
        except: pass
        if COMMENTARY == 'true':
            try: url = episode['video_urls'][RATIO]['en_US']['video_url_commentary']
            except: pass
        icon = episode['img_url']
        desc = episode['description']
        duration = episode['duration']
        aired = episode['airDate']
        season = str(episode['season']).zfill(2) 
        episode = str(episode['episode']).zfill(2)         

        info = {'plot':desc,'tvshowtitle':LOCAL_STRING(30000), 'season':season, 'episode':episode, 'title':title,'originaltitle':title,'duration':duration,'aired':aired,'genre':LOCAL_STRING(30002)}
        
        addEpisode(title,url,title,icon,FANART,info)



def getStream(curation_id):
    '''
    GET https://ios-api-us.crackle.com/Service.svc/curation/30534/US?format=json HTTP/1.1
    Host: ios-api-us.crackle.com
    Accept: */*
    Connection: keep-alive
    If-None-Match: "41776591-3885-408a-a4ee-020a80c84025"
    Cookie: GR=348
    Accept-Language: en-us
    Authorization: 6C34892ACD3B811EA91807E07BE7046E19DAA9D7|201703232017|22|1
    Accept-Encoding: gzip, deflate
    User-Agent: Crackle/7.60 CFNetwork/808.3 Darwin/16.3.0
    '''
    url = 'http://ios-api-us.crackle.com/Service.svc/curation/'+curation_id+'/US' 
    url += '?format=json'
    
    req = urllib2.Request(url)
    req.add_header("Accept", "*/*")
    req.add_header("Accept-Encoding", "deflate")
    req.add_header("Accept-Language", "en-us")
    req.add_header("Connection", "keep-alive")        
    req.add_header("User-Agent", UA_CRACKLE)
    response = urllib2.urlopen(req)   
    json_source = json.load(response)                       
    response.close()  
    media_id = json_source['Result']['Items'][0]['MediaInfo']['Id']
    '''
    GET https://ios-api-us.crackle.com/Service.svc/details/media/2489564/US?format=json HTTP/1.1
    Host: ios-api-us.crackle.com
    Connection: keep-alive
    Accept: */*
    User-Agent: Crackle/7.60 CFNetwork/808.3 Darwin/16.3.0
    Accept-Language: en-us
    Authorization: 127DE6571887D314D5BF86EC39DABA4B7CB2C80B|201703231759|22|1
    Accept-Encoding: gzip, deflate
    '''
    #url = 'http://ios-api-us.crackle.com/Service.svc/details/media/2489564/US'    
    url = 'http://ios-api-us.crackle.com/Service.svc/details/media/'+media_id+'/US'  
    url += '?format=json'
    
    req = urllib2.Request(url)
    req.add_header("Accept", "*/*")
    req.add_header("Accept-Encoding", "deflate")
    req.add_header("Accept-Language", "en-us")
    req.add_header("Connection", "keep-alive")        
    req.add_header("User-Agent", UA_CRACKLE)
    response = urllib2.urlopen(req)   
    json_source = json.load(response)                       
    response.close()  

    
    for stream in json_source['MediaURLs']:
        if 'AppleTV' in stream['Type']:
            stream_url = stream['Path']
            stream_url = stream_url[0:stream_url.index('.m3u8')]+'.m3u8'
            break

    stream_url += '|User-Agent='+UA_CRACKLE
    listitem = xbmcgui.ListItem(path=stream_url)
    xbmcplugin.setResolvedUrl(addon_handle, True, listitem)
        


def addStream(name, link_url, stream_type, icon,fanart,info=None):
    ok=True
    u=sys.argv[0]+"?id="+urllib.quote_plus(link_url)+"&mode="+str(102)
    liz=xbmcgui.ListItem(name)
    liz.setArt({'icon': ICON, 'thumb': icon, 'fanart': fanart})    
    liz.setProperty("IsPlayable", "true")
    liz.setInfo( type="Video", infoLabels={ "Title": name } )
    if info != None:
        liz.setInfo( type="Video", infoLabels=info) 
    ok=xbmcplugin.addDirectoryItem(handle=addon_handle,url=u,listitem=liz,isFolder=False)
    xbmcplugin.setContent(addon_handle, stream_type)    
    return ok


def addDir(name,url,mode,iconimage,fanart=None,info=None): 
    params = get_params()      
    ok=True    
    u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)
    liz=xbmcgui.ListItem(name)
    liz.setArt({'icon': ICON, 'thumb': iconimage, 'fanart': fanart})    
    if info != None:
        liz.setInfo( type="Video", infoLabels=info)     
    ok=xbmcplugin.addDirectoryItem(handle=addon_handle,url=u,listitem=liz,isFolder=True)    
    xbmcplugin.setContent(addon_handle, 'tvshows')
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