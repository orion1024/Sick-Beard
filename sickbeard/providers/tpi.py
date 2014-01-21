# -*- coding: latin-1 -*-
# Author: orion1024 <orion1024@gmail.com>
# URL: http://code.google.com/p/sickbeard/
#
# This file is part of Sick Beard.
#
# Sick Beard is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Sick Beard is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Sick Beard.  If not, see <http://www.gnu.org/licenses/>.

from bs4 import BeautifulSoup
from sickbeard import classes, show_name_helpers, logger
from sickbeard.common import Quality
import generic
import cookielib
import sickbeard
import urllib
import urllib2
import re

class TPIProvider(generic.TorrentProvider):

    def __init__(self):
        
        generic.TorrentProvider.__init__(self, "TPI")

        self.supportsBacklog = True
        
        self.cj = cookielib.CookieJar()
        self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cj))
        
        self.url = "https://www.thepirateisland.net"
        
        self.login_done = False
        self.failed_login_logged = False
        self.successful_login_logged = False
        
    def isEnabled(self):
        return sickbeard.TPI
    
    def getSearchParams(self, searchString, audio_lang, french=None, fullSeason=False):

        results = []
        if audio_lang == "en" and french==None:
            results.append( urllib.urlencode( {'search': searchString, 'parent_cat' : "Séries VOSTFR", 'cat': 0, 'incldead' : 0, 'lang' : 1  } ))
            results.append( urllib.urlencode( {'search': searchString, 'parent_cat' : "Séries VOSTFR", 'cat': 0, 'incldead' : 0, 'lang' : 2  } ))
            results.append( urllib.urlencode( {'search': searchString, 'parent_cat' : "Séries VO", 'cat': 0, 'incldead' : 0, 'lang' : 1  } ))
            if not fullSeason: # there is a bug in TPI search, when selecting category Series Multi the search returns single episodes torrents even when we are looking for full season.
               results.append( urllib.urlencode( {'search': searchString, 'parent_cat' : "Séries Multi", 'cat': 0, 'incldead' : 0, 'lang' : 0  } ))
        elif audio_lang == "en" and french:
            results.append( urllib.urlencode( {'search': searchString, 'parent_cat' : "Séries VOSTFR", 'cat': 0, 'incldead' : 0, 'lang' : 1  } ))
            results.append( urllib.urlencode( {'search': searchString, 'parent_cat' : "Séries VOSTFR", 'cat': 0, 'incldead' : 0, 'lang' : 2  } ))
        elif audio_lang == "fr" or french:
            results.append( urllib.urlencode( {'search': searchString, 'parent_cat' : "Séries VF", 'cat': 0, 'incldead' : 0, 'lang' : 0  } ))
            if not fullSeason: # there is a bug in TPI search, when selecting category Series Multi the search returns single episodes torrents even when we are looking for full season.
               results.append( urllib.urlencode( {'search': searchString, 'parent_cat' : "Séries Multi", 'cat': 0, 'incldead' : 0, 'lang' : 0  } ))
        else:
            results.append( urllib.urlencode( {'search': searchString, 'parent_cat' : "Séries VOSTFR", 'cat': 0, 'incldead' : 0, 'lang' : 0  } ))
            results.append( urllib.urlencode( {'search': searchString, 'parent_cat' : "Séries VO", 'cat': 0, 'incldead' : 0, 'lang' : 0  } ))
            if not fullSeason: # there is a bug in TPI search, when selecting category Series Multi the search returns single episodes torrents even when we are looking for full season.
               results.append( urllib.urlencode( {'search': searchString, 'parent_cat' : "Séries Multi", 'cat': 0, 'incldead' : 0, 'lang' : 0  } ))
            results.append( urllib.urlencode( {'search': searchString, 'parent_cat' : "Séries VF", 'cat': 0, 'incldead' : 0, 'lang' : 0  } ))
        return results
        
    def _get_season_search_strings(self, show, season):

        showNam = show_name_helpers.allPossibleShowNames(show)
        showNames = list(set(showNam))
        results = []
        for showName in showNames:
            results.extend( self.getSearchParams(showName + " saison%d" % season, show.audio_lang, fullSeason=True))
            results.extend( self.getSearchParams(showName + " season%d" % season, show.audio_lang, fullSeason=True))
            results.extend( self.getSearchParams(showName + " saison %d" % season, show.audio_lang, fullSeason=True))
            results.extend( self.getSearchParams(showName + " season %d" % season, show.audio_lang, fullSeason=True))
            results.extend( self.getSearchParams(showName + " saison%02d" % season, show.audio_lang, fullSeason=True))
            results.extend( self.getSearchParams(showName + " season%02d" % season, show.audio_lang, fullSeason=True))
            results.extend( self.getSearchParams(showName + " saison %02d" % season, show.audio_lang, fullSeason=True))
            results.extend( self.getSearchParams(showName + " season %02d" % season, show.audio_lang, fullSeason=True))
            results.extend( self.getSearchParams(showName + ".S%02d." % season, show.audio_lang, fullSeason=True))
        return results

    def _get_episode_search_strings(self, ep_obj, french=None):

        showNam = show_name_helpers.allPossibleShowNames(ep_obj.show)
        showNames = list(set(showNam))
        results = []
        for showName in showNames:
            results.extend( self.getSearchParams( "%s S%02dE%02d" % ( showName, ep_obj.scene_season, ep_obj.scene_episode), ep_obj.show.audio_lang, french ))
            results.extend( self.getSearchParams( "%s %dx%02d" % ( showName, ep_obj.scene_season, ep_obj.scene_episode ), ep_obj.show.audio_lang, french ))
        return results
    
    def _get_title_and_url(self, item):
        return (item.title, item.url)
    
    def getQuality(self, item):
        return item.getQuality()
    
    def _doLogin(self, login, password):

        # TPI is using an antibot slide bar. However it can be bypassed easily... Credits goes to drew010 (see http://stackoverflow.com/questions/10609201/qaptcha-is-it-effective)
        fake_qaptcha_key = 'thisIsAFakeKey12345';  # arbitrary qaptcha_key - normally by client JavaScript
        
        # fetch the form - this creates a PHP session and gives us a cookie (yum)
        r = self.opener.open(self.url + '/connexion.php')

        # This step is important - this stores a "qaptcha_key" in the PHP session that matches our session cookie
        # We can make the key up in this step, it doesn't matter what it is or where it came from
        simulateQaptchaSlideData = urllib.urlencode({'action': 'qaptcha', 'qaptcha_key' : fake_qaptcha_key})

        req = urllib2.Request(self.url + '/php/Qaptcha.jquery.php', simulateQaptchaSlideData, 
                             {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:26.0) Gecko/20100101 Firefox/26.0'})
        r = self.opener.open(req)

        data = urllib.urlencode({'username': login, 'password' : password, fake_qaptcha_key : '', 'submit' : 'Connexion', 'returnto' : '/'})
        
        req = urllib2.Request(self.url + '/connexion.php', data, 
                                 {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:26.0) Gecko/20100101 Firefox/26.0',
                                 'Referer' : 'https://www.thepirateisland.net/connexion.php?returnto=Lw==' })

        r = self.opener.open(req)
        
        for index, cookie in enumerate(self.cj):
            if (cookie.name == "pass"): self.login_done = True
                                
        if not self.login_done and not self.failed_login_logged:
            logger.log(u"Unable to login to TPI. Please check username and password.", logger.WARNING) 
            self.failed_login_logged = True
        
        if self.login_done and not self.successful_login_logged:
            logger.log(u"Login to TPI successful", logger.MESSAGE) 
            self.successful_login_logged = True        

    def _doSearch(self, searchString, show=None, season=None, french=None):

        
        if not self.login_done:
            self._doLogin( sickbeard.TPI_USERNAME, sickbeard.TPI_PASSWORD )

        results = []

        searchUrl = self.url + '/parcourir.php?' + searchString.replace('!','')
 
        logger.log(u"Search string: " + searchUrl, logger.DEBUG)
        
        r = self.opener.open( searchUrl )

        soup = BeautifulSoup( r, "html.parser" )

        resultsTable = soup.find("table", { "class" : "ttable_headinner" })
        if resultsTable:

            rows = resultsTable.findAll("tr", { "class" : "t-row" })
    
            for row in rows:

                link = row.find("a", title=True)
                title = link['title']

                downloadURL = row.find("a",href=re.compile("\.torrent"))['href']
                
                
                quality = Quality.nameQuality( title )
                if quality==Quality.UNKNOWN and title:
                    if '720p' not in title.lower() and '1080p' not in title.lower():
                        quality=Quality.SDTV
                if show and french==None:
                    results.append( TPISearchResult( self.opener, title, downloadURL, quality, str(show.audio_lang) ) )
                elif show and french:
                    results.append( TPISearchResult( self.opener, title, downloadURL, quality, 'fr' ) )
                else:
                    results.append( TPISearchResult( self.opener, title, downloadURL, quality ) )
        
        return results
    
    def getResult(self, episodes):
        """
        Returns a result of the correct type for this provider
        """
        result = classes.TorrentDataSearchResult(episodes)
        result.provider = self

        return result    
    
class TPISearchResult:
    
    def __init__(self, opener, title, url, quality, audio_langs=None):
        self.opener = opener
        self.title = title
        self.url = url
        self.quality = quality
        self.audio_langs=audio_langs
        
    def getNZB(self):
        return self.opener.open( self.url , 'wb').read()

    def getQuality(self):
        return self.quality

provider = TPIProvider()
