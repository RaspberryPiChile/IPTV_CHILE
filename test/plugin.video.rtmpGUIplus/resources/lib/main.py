#!/usr/bin/env python
# -*- coding: utf-8 -*-
# main.py - rtmpGUI extension withEPG
# (C) 2012 HansMayer,BlueCop - http://supertv.3owl.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
import urllib, urllib2, cookielib
import string, os, re, time, sys

import xbmc, xbmcgui, xbmcplugin, xbmcaddon
__settings__   = xbmcaddon.Addon()

from aes import AESCtr
from epg import *

try:
    try:
        raise
        import xml.etree.cElementTree as ElementTree
    except:
        from xml.etree import ElementTree
except:
    try:
        from elementtree import ElementTree
    except:
        dlg = xbmcgui.Dialog()
        dlg.ok('ElementTree missing', 'Please install the elementree addon.',
                'http://tinyurl.com/xmbc-elementtree')
        sys.exit(0)

def addFolder(BASE, source=None, lang='', totalItems=0):
    if not lang:
        #title=urllib.unquote(BASE[source].split('/')[-1][:-4])
        title = BASE[source][1]
    else:
        title=lang
    item=xbmcgui.ListItem(title, iconImage=os.path.join(xbmcaddon.Addon().getAddonInfo('path'),'icon.png'))
    item.setInfo( type="Video", infoLabels={ "Title": title })
    xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=sys.argv[0]+"?src="+str(source)+"&lang="+lang,listitem=item,isFolder=True,totalItems=totalItems)

def addFolderC(BASE, source=None, title='', i=0, totalItems=0, thumb=''):
    item=xbmcgui.ListItem(title, iconImage=thumb)
    item.setInfo( type="Video", infoLabels={ "Title": title })
    xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=sys.argv[0]+"?src="+str(source)+"&channel="+str(i),listitem=item,isFolder=True,totalItems=totalItems)

def get_params():
    param=[]
    paramstring=sys.argv[2]
    if len(paramstring)>=2:
        params=sys.argv[2]
        cleanedparams=params.replace('?','')
        if (params[-1]=='/'):
            params=params[0:-2]
        pairsofparams=cleanedparams.split('&')
        param={}
        for i in pairsofparams:
            splitparams={}
            splitparams=i.split('=')
            if (len(splitparams))==2:
                param[splitparams[0]]=splitparams[1]
    return param

def checkAutoupdateEPG():
    if os.popen('uname').read().strip() == 'Darwin':
        if not os.path.exists(os.path.expanduser('~/Library/LaunchAgents/com.xbmc.rtmpGUI.plist')):
            launch = True
        else:
            launch = False
        cmd='cp "'+os.path.join(xbmcaddon.Addon().getAddonInfo('path'),'resources/com.xbmc.rtmpGUI.plist')
        os.system(cmd+'" "'+os.path.expanduser('~/Library/LaunchAgents/')+'"')
        if launch:
            os.system('launchctl load "'+os.path.expanduser('~/Library/LaunchAgents/com.xbmc.rtmpGUI.plist')+'"')
            
def playItem(params):
    listitem = xbmcgui.ListItem(label=urllib.unquote(params['title']), iconImage=urllib.unquote(params['logo']), path=params['link'])
    xbmcplugin.setResolvedUrl(handle=int(sys.argv[1]), succeeded=True, listitem=listitem)
    xbmc.executebuiltin("Container.SetViewMode(503)")
    
def filmOnUpdate(params):
    link=urllib.unquote(params['link'])
    chanid=link.split(' ')[0].split('?')[0].split('live')[1]
    quality=link.split(' ')[1].split('=')[1].split('.')[1]
    phpsessid=downloadSocket('www.filmon.com',80).fetch('GET /ajax/getChannelInfo HTTP/1.1\r\nHost: www.filmon.com\r\nConnection:close\r\nUser-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_3) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.151 Safari/535.19\r\n\r\n').split('PHPSESSID=')[1].split(";")[0]
    headers=[('Origin','http://www.filmon.com'),('Referer','http://www.filmon.com/tv/htmlmain/'),('X-Requested-With','XMLHttpRequest'),('Accept','application/json, text/javascript, */*'),('Connection','keep-alive'),('Cookie','disable-edgecast=1; viewed_site_version_cookie=html;PHPSESSID='+phpsessid+";")]
    a=getURL('http://www.filmon.com/ajax/getChannelInfo', post=urllib.urlencode({'channel_id':chanid, 'quality':quality}),headers=headers,ct=True)

    params['link'] = json.loads(a)[0]['serverURL']+' playpath='+json.loads(a)[0]['streamName']+" app=live/"+json.loads(a)[0]['serverURL'].split('/')[-1]+" "+" ".join(link.split(' ')[2:])
    playItem(params)

    
def update45ESToken(params):
    link=urllib.unquote(params['link'])
    playpath=re.findall('playpath=(?P<playpath>.*?) ',link)[0]
    rtmplink = link.split(' ')[0]
    directo=AESCtr().encrypt(getURL('http://servicios.telecinco.es/tokenizer/clock.php')+";"+playpath+";0;0", "xo85kT+QHz3fRMcHMXp9cA", 256)
    data=getURL('http://servicios.telecinco.es/tokenizer/tk3.php',post=urllib.urlencode({'id':playpath,'startTime':'0','directo':directo,'endTime':'endTime'}))
    #params['link'] = link.replace('playpath='+playpath, 'playpath='+ElementTree.XML(data).findtext('file'))
    xdata = ElementTree.XML(data)
    params['link'] = link.replace('playpath='+playpath, 'playpath='+xdata.findtext('file')).replace(rtmplink, xdata.findtext('stream'))
    playItem(params)
    
def listSources(BASE):
    if len(BASE) < 2:
        listLanguages(BASE)
        return

    for source in BASE:
        addFolder(BASE,BASE.index(source),totalItems=len(BASE))
    xbmc.executebuiltin("Container.SetViewMode(502)")
    xbmcplugin.endOfDirectory( handle=int( sys.argv[ 1 ] ) )

    
def listChannels(BASE,src=0):
    xml=getURL(BASE[int(src)][0],None)
    #tree = ElementTree.XML(xml)
    tree = ElementTree.parse(StringIO(xml)).getroot()
    languages = tree.findall('channel')

    if len(languages) < 2:
        listVideos(BASE,src, 0, 0)
        return
    i = 0
    for lang in languages:
        addFolderC(BASE,src, lang.findtext('name'), i, totalItems=len(languages), thumb=lang.findtext('thumbnail', "DefaultTVShows.png"))
        i += 1
    xbmc.executebuiltin("Container.SetViewMode(502)")
    xbmcplugin.endOfDirectory( handle=int( sys.argv[ 1 ] ) )
    
    
    
def listLanguages(BASE,src=0):
    xml=getURL(BASE[int(src)][0],None)
    #tree = ElementTree.XML(xml)
    tree = ElementTree.parse(StringIO(xml)).getroot()
    if len(tree.findall('channel')) > 0:
        listChannels(BASE,src)
        return
    streams = tree.findall('stream')
    languages = []
    for stream in streams:
        language = stream.findtext('language').strip()
        if not language in languages and language.find('Link Down') == -1:
            languages.append(language)
            
    languages = list(set(languages))
    languages.sort()

    if len(languages) < 2:
        listVideos(BASE,src, languages[0])
        return

    for lang in languages:
        addFolder(BASE,src, lang, totalItems=len(languages))
    xbmc.executebuiltin("Container.SetViewMode(502)")
    xbmcplugin.endOfDirectory( handle=int( sys.argv[ 1 ] ) )


def listVideos(BASE,src=0,lang='',chan=-1):
    xml=getURL(BASE[int(src)][0],None)
    #tree = ElementTree.XML(xml)
    tree = ElementTree.parse(StringIO(xml)).getroot()

    hasEPG=False
    newS=[]
    if chan > -1:
        newS = tree.findall('channel')
        print newS
        newS = newS[chan].findall('items')[0].findall('item')
    else:
        streams = tree.findall('stream')
        for stream in streams:
            language = stream.findtext('language').strip()
            if language == lang and language.find('Link Down') == -1 :
                newS.append(stream)
    
    for stream in newS:
        title = '[B]'+stream.findtext('title')+'[/B]'
        desc = title
        epgid=stream.findtext('epgid', None)
        if epgid:
            ep=epgid.split(":")
            if ep[0] in EPGs.keys():
				e=EPGs[ep[0]](ep[1])
				hasEPG = True
				desc = ""
				epg=e.getEntries()
				i=len(epg)
				for e in epg:
				    if (__settings__.getSetting("show24h") == 'false'):
				        desc += e[1].strftime("%I:%M")+'-'+e[2].strftime("%I:%M")+":\n"+e[0]+u"\n\n"
				    else:
				        desc += e[1].strftime("%H:%M")+'-'+e[2].strftime("%H:%M")+":\n"+e[0]+u"\n\n"
				if len(epg) > 0:
				    title +=' - '+epg[0][0]
        rtmplink = stream.findtext('link',' ').strip()
        if rtmplink[:4] == 'rtmp':
            if stream.findtext('playpath'):
                rtmplink += ' playpath='+stream.findtext('playpath').strip()
            if stream.findtext('swfUrl'):
                rtmplink += ' swfurl='+stream.findtext('swfUrl').strip()
            if stream.findtext('pageUrl'):
                rtmplink += ' pageurl='+stream.findtext('pageUrl').strip()
            if stream.findtext('proxy'):
                rtmplink += ' socks='+stream.findtext('proxy').strip()
            if stream.findtext('advanced','').find('live=') == -1 and rtmplink.find('mms://') == -1 and rtmplink.find('http://') != 0:
                rtmplink += ' live=1 '
            if rtmplink[:4] == 'rtmp':
                rtmplink += ' timeout=30 '+stream.findtext('advanced','').replace('-v','').replace('live=1','').replace('live=true','')
            if (__settings__.getSetting("has_updated_librtmp") == 'true'):
                rtmplink = rtmplink.replace('-x ',"swfsize=").replace('-w ','swfhash=')    
        logo=stream.findtext('logourl', "DefaultTVShows.png")
        if chan > -1:
            logo=stream.findtext('thumbnail', "DefaultTVShows.png")
        item=xbmcgui.ListItem(title, iconImage=logo)
        infolabels = { "title": title, "plot": desc, "plotoutline": desc, "tvshowtitle": title, "originaltitle": title}
        item.setInfo( type="video", infoLabels=infolabels )
        item.setProperty('IsPlayable', 'true')
        xbmcplugin.setContent( handle=int( sys.argv[ 1 ] ), content='movies' )
        if stream.findtext('swfUrl') == 'http://www.filmon.com/tv/modules/FilmOnTV/files/flashapp/filmon/FilmonPlayer.swf?v=f':
            rtmplink = sys.argv[0]+"?tk=filmon&link="+urllib.quote(rtmplink)+"&title="+urllib.quote(title.encode('utf-8'))+"&logo="+urllib.quote(logo)
        if stream.findtext('swfUrl') == 'http://static1.tele-cinco.net/comun/swf/playerCuatro.swf':
            rtmplink = sys.argv[0]+"?tk=telecinco&link="+urllib.quote(rtmplink)+"&title="+urllib.quote(title.encode('utf-8'))+"&logo="+urllib.quote(logo)
        xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=rtmplink.strip(),listitem=item,isFolder=False,totalItems=len(newS))
            
    if hasEPG:
        xbmc.executebuiltin("Container.SetViewMode(503)")
    else:
        xbmc.executebuiltin("Container.SetViewMode(502)")
    
            
    xbmcplugin.endOfDirectory( handle=int( sys.argv[ 1 ] ) )

def main(BASE):
    parms=get_params()
    if 'link' in parms and 'tk' in parms:
        if parms['tk'] == 'telecinco':
            update45ESToken(parms)
        elif parms['tk'] == 'filmon':
            filmOnUpdate(parms)
    if "src" in parms and 'lang' in parms and parms['lang']:
        listVideos(BASE,parms['src'], parms['lang'])
    elif "src" in parms and 'channel' in parms and parms['channel']:
        listVideos(BASE,parms['src'], chan=int(parms['channel']))
    elif 'src' in parms:
        listLanguages(BASE,parms['src'])
    else:
        checkAutoupdateEPG()
        listSources(BASE)