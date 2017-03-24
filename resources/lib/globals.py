import sys, os
import xbmc, xbmcplugin, xbmcgui, xbmcaddon
import urllib, urllib2
import json
import base64, hmac, hashlib
from datetime import datetime



addon_handle = int(sys.argv[1])
ADDON = xbmcaddon.Addon(id='plugin.video.crackle')
ROOTDIR = ADDON.getAddonInfo('path')
FANART = ROOTDIR+"/resources/media/fanart.jpg"
ICON = ROOTDIR+"/resources/media/icon.png"

#Addon Settings 
LOCAL_STRING = ADDON.getLocalizedString
UA_CRACKLE = 'Crackle/7.60 CFNetwork/808.3 Darwin/16.3.0'
UA_WEB = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.110 Safari/537.36'

def mainMenu():    
    addDir('Movies','/movies',101,ICON)
    addDir('TV','/tv',100,ICON)


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



def listShows():    
    '''
    GET https://ios-api-us.crackle.com/Service.svc/browse/shows/full/all/alpha-asc/US?pageSize=24&pageNumber=1&format=json HTTP/1.1
    Host: ios-api-us.crackle.com
    Connection: keep-alive
    If-None-Match: "01f02ff7-6285-4399-91dd-e7474f6b2827"
    Accept: */*
    User-Agent: Crackle/7.60 CFNetwork/808.3 Darwin/16.3.0
    Accept-Language: en-us
    Authorization: 2F29DC88BB9F2BC708D7B85779C8ED00C4BB2892|201703240126|22|1
    Accept-Encoding: gzip, deflate
    '''
    url = 'http://ios-api-us.crackle.com/Service.svc/browse/shows/full/all/alpha-asc/US'
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
    

    for show in json_source['Entries']:        
        title = show['Title']
        url = str(show['ID'])
        icon = show['ChannelArtTileLarge']
        fanart = show['Images']['Img_1920x1080']
        info = None
        info = {'plot':show['Description'],
                'genre':show['Genre'], 
                'year':show['ReleaseYear'], 
                'mpaa':show['Rating'], 
                'title':title,
                'originaltitle':title,
                'duration':show['DurationInSeconds']
                }

        #addStream(title,url,'tvshows',icon,fanart,info)
        addDir(title,url,103,icon,fanart,info)


def getEpisodes(channel):    
    '''
    GET https://ios-api-us.crackle.com/Service.svc/channel/1515/playlists/all/US?format=json HTTP/1.1
    Host: ios-api-us.crackle.com
    Connection: keep-alive
    Accept: */*
    User-Agent: Crackle/7.60 CFNetwork/808.3 Darwin/16.3.0
    Accept-Language: en-us
    Authorization: 36A76467B6DD721D3BB86257E564D3315F79EC1D|201703240126|22|1
    Accept-Encoding: gzip, deflate
    '''
    url = 'http://ios-api-us.crackle.com/Service.svc/channel/'+str(channel)+'/playlists/all/US?format=json'
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
    

    for episode in json_source['Playlists'][0]['Items']:
        episode = episode['MediaInfo']
        title = episode['Title']
        id = str(episode['Id'])
        icon = episode['Images']['Img_460x460']
        fanart = episode['Images']['Img_1920x1080']
        info = None
        info = {'plot':episode['Description'],
                #'genre':episode['Genre'], 
                'year':episode['ReleaseYear'], 
                'mpaa':episode['Rating'], 
                'title':title,
                'originaltitle':title,
                'duration':episode['Duration'],
                'season':episode['Season'],
                'episode':episode['Episode']
                }

        addStream(title,id,'tvshows',icon,fanart,info)
        #addDir(title,url,103,icon,fanart,info)




def getStream(id):   

    '''
    Get playlist
    GET https://ios-api-us.crackle.com/Service.svc/channel/451/playlists/all/US?format=json HTTP/1.1
    Host: ios-api-us.crackle.com
    Accept: */*
    Connection: keep-alive
    Cookie: GR=348
    User-Agent: Crackle/7.60 CFNetwork/808.3 Darwin/16.3.0
    Accept-Language: en-us
    Authorization: BCF1ED28805495CE259DE7D3DEC2676F1FDEA7DB|201703232219|22|1
    Accept-Encoding: gzip, deflate
    
    url = 'http://ios-api-us.crackle.com/Service.svc/channel/'+org_id+'/playlists/all/US?format=json'
    req = urllib2.Request(url)
    req.add_header("Accept", "*/*")
    req.add_header("Accept-Encoding", "deflate")
    req.add_header("Accept-Language", "en-us")
    req.add_header("Connection", "keep-alive")        
    req.add_header("User-Agent", UA_CRACKLE)
    response = urllib2.urlopen(req)   
    json_source = json.load(response)                       
    response.close()  
    media_id = str(json_source['Playlists'][0]['Items'][0]['MediaInfo']['Id'])
    playlist_id = str(json_source['Playlists'][0]['PlaylistId'])
    '''
    
    '''
    get media id
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
    
    #url = 'http://ios-api-us.crackle.com/Service.svc/curation/'+curation_id+'/US' 
    #url += '?format=json'    
    url = 'https://ios-api-us.crackle.com/Service.svc/curation/'+curation_id+'/US?format=json'
    req = urllib2.Request(url)
    req.add_header("Accept", "*/*")
    req.add_header("Accept-Encoding", "deflate")
    req.add_header("Accept-Language", "en-us")
    req.add_header("Connection", "keep-alive")        
    req.add_header("User-Agent", UA_CRACKLE)
    response = urllib2.urlopen(req)   
    json_source = json.load(response)                       
    response.close()  
    media_id = str(json_source['Result']['Items'][0]['MediaInfo']['Id'])
    '''

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
    #url = 'https://ios-api-us.crackle.com/Service.svc/details/media/'+id+'/US?format=json'    
    #url = 'https://wp-api-us.crackle.com/Service.svc/details/media/'+id+'/US?format=json'    
    url = 'http://android-api-us.crackle.com/Service.svc/details/media/'+id+'/US?format=json'

    xbmc.log('TEST!!!')
    xbmc.log(url)
    


    req = urllib2.Request(url)
    req.add_header("Accept", "*/*")
    req.add_header("Accept-Encoding", "deflate")
    req.add_header("Accept-Language", "en-us")
    req.add_header("Connection", "keep-alive")        
    req.add_header("User-Agent", UA_CRACKLE)
    #req.add_header("Authorization", "823CA68EF08AC9F42AA086E9F63F6753739792D8|201703232253|22|1")
    req.add_header("Authorization", getAuth(url))
    req.add_header("Cookie", "GR=348")
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
        

def getAuth(url):
    '''
    String encodedUrl = null;
    String timeStamp = createTimeStampString(new Date());
    try {
        encodedUrl = calcHmac(url + "|" + timeStamp) + "|" + timeStamp + "|" + ApplicationConstants.getVendorID();
    } catch (Exception e) {
        e.printStackTrace();
    }
    return encodedUrl;
    '''
    
    '''
    SimpleDateFormat df = new SimpleDateFormat("yyyyMMddHHmm");
    df.setTimeZone(TimeZone.getTimeZone("UTC"));
    return df.format(date);
    '''
    
    '''
    SecretKeySpec sk = new SecretKeySpec(ApplicationConstants.getVendorKey().getBytes(), "HmacMD5");
    Mac mac = Mac.getInstance("HmacMD5");
    mac.init(sk);
    return byteToString(mac.doFinal(src.getBytes()));

    public static String getVendorKey() {
    if (!Application.getInstance().isTablet()) {
        return PHONE_VENDOR_KEY;
    }
    if (Application.isAmazonFireTV()) {
        return "JLMLKPUFQNZYTZQX";
    }
    if (Application.isFanhattan()) {
        return "QWMJCYOZUYONPXPR";
    }
    return "MIRNPSEZYDAQASLX";
    }
    '''
    phone_vendor_key = 'QWXRHTCJPOGKBJKO'    
    #phone_vendor_key = '52AE53EBA1B0E1578E7DE64B53E96855'
    phone_vendor_key = hashlib.md5(bytearray(phone_vendor_key)).digest()
    vendor_id = '24'
    timestamp = datetime.utcnow().strftime('%Y%m%d%H%M')
    temp = url+"|"+timestamp        
    test = hmac.new(phone_vendor_key,  temp, hashlib.sha1)    
    encodedUrl = str(test.hexdigest()).upper() + "|" + timestamp + "|" + vendor_id
    #Should be 40 in length
    xbmc.log(encodedUrl)

    return encodedUrl


    '''
    nonce = str(uuid.uuid4())
    epochtime = str(int(time.time() * 1000))        
    authorization = request_method + " requestor_id="+self.requestor_id+", nonce="+nonce+", signature_method=HMAC-SHA1, request_time="+epochtime+", request_uri="+request_uri
    signature = hmac.new(self.private_key , authorization, hashlib.sha1)
    signature = base64.b64encode(signature.digest())
    authorization += ", public_key="+self.public_key+", signature="+signature
    '''


def addStream(name, id, stream_type, icon,fanart,info=None):
    ok=True
    u=sys.argv[0]+"?id="+urllib.quote_plus(id)+"&mode="+str(102)
    liz=xbmcgui.ListItem(name)
    liz.setArt({'icon': ICON, 'thumb': icon, 'fanart': fanart})    
    liz.setProperty("IsPlayable", "true")
    liz.setInfo( type="Video", infoLabels={ "Title": name } )
    if info != None:
        liz.setInfo( type="Video", infoLabels=info) 
    ok=xbmcplugin.addDirectoryItem(handle=addon_handle,url=u,listitem=liz,isFolder=False)
    xbmcplugin.setContent(addon_handle, stream_type)    
    return ok


def addDir(name,id,mode,iconimage,fanart=None,info=None): 
    params = get_params()      
    ok=True    
    u=sys.argv[0]+"?id="+urllib.quote_plus(id)+"&mode="+str(mode)
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