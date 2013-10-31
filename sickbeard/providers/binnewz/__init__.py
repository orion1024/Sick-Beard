# -*- coding: latin-1 -*-
# Author: Guillaume Serre <guillaume.serre@gmail.com>
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

import re
import urllib
import urllib2

from binsearch import BinSearch
from nzbclub import NZBClub
from nzbindex import NZBIndex
from bs4 import BeautifulSoup
from sickbeard import logger, classes, show_name_helpers, db
from sickbeard.providers import generic
from sickbeard.common import Quality
from sickbeard.exceptions import ex
import sickbeard


class BinNewzProvider(generic.NZBProvider):
    allowedGroups = {
        'abmulti': 'alt.binaries.multimedia',
        'abtvseries': 'alt.binaries.tvseries',
        'abtv': 'alt.binaries.tv',
        'a.b.teevee': 'alt.binaries.teevee',
        'abstvdivxf': 'alt.binaries.series.tv.divx.french',
        'abhdtvx264fr': 'alt.binaries.hdtv.x264.french',
        'abmom': 'alt.binaries.mom',
        'abhdtv': 'alt.binaries.hdtv',
        'abboneless': 'alt.binaries.boneless',
        'abhdtvf': 'alt.binaries.hdtv.french',
        'abhdtvx264': 'alt.binaries.hdtv.x264',
        'absuperman': 'alt.binaries.superman',
        'abechangeweb': 'alt.binaries.echange-web',
        'abmdfvost': 'alt.binaries.movies.divx.french.vost',
        'abdvdr': 'alt.binaries.dvdr',
        'abmzeromov': 'alt.binaries.movies.zeromovies',
        'abcfaf': 'alt.binaries.cartoons.french.animes-fansub',
        'abcfrench': 'alt.binaries.cartoons.french',
        'abgougouland': 'alt.binaries.gougouland',
        'abroger': 'alt.binaries.roger',
        'abtatu': 'alt.binaries.tatu',
        'abstvf': 'alt.binaries.series.tv.french',
        'abmdfreposts': 'alt.binaries.movies.divx.french.reposts',
        'abmdf': 'alt.binaries.movies.french',
        'ab.aa': 'alt.binaries.aa',
        'abspectdf': 'alt.binaries.spectacles.divx.french'
    }

    qualityCategories = {
        3: ['24', '7', '56'],
        500: ['44', '53']
    }

    qualityMinSize = {
        (Quality.SDTV, Quality.SDDVD): 130,
        Quality.HDTV: 500,
        (Quality.HDWEBDL, Quality.HDBLURAY, Quality.FULLHDBLURAY, Quality.FULLHDTV, Quality.FULLHDWEBDL): 600
    }

    url = "http://www.binnews.in/"
    supportsBacklog = True
    nzbDownloaders = [BinSearch(), NZBIndex(), NZBClub()]

    def __init__(self):
        generic.NZBProvider.__init__(self, "BinnewZ")

    def isEnabled(self):
        return sickbeard.BINNEWZ

    def _get_season_search_strings(self, show, season, episode=None):
        showNam = show_name_helpers.allPossibleShowNames(show)
        showNames = list(set(showNam))
        result = []
        global globepid        
        global searchstringlist
        searchstringlist=[]
        globepid = show.tvdbid
        for showName in showNames:
            result.append(showName + ".saison %2d" % season)
        return result

    def _get_episode_search_strings(self, ep_obj, french=None):
        strings = []
        showNam = show_name_helpers.allPossibleShowNames(ep_obj.show)
        showNames = list(set(showNam))
        global globepid
        global searchstringlist
        searchstringlist=[]
        myDB = db.DBConnection()
        epidr = myDB.select("SELECT episode_id from tv_episodes where tvdbid=?", [ep_obj.tvdbid])
        globepid = epidr[0][0]
        for showName in showNames:
            strings.append("%s S%02dE%02d" % (showName, ep_obj.scene_season, ep_obj.scene_episode))
            strings.append("%s S%02dE%d" % (showName, ep_obj.scene_season, ep_obj.scene_episode))
            strings.append("%s S%dE%02d" % (showName, ep_obj.scene_season, ep_obj.scene_episode))
            strings.append("%s %dx%d" % (showName, ep_obj.scene_season, ep_obj.scene_episode))
            strings.append("%s S%02d E%02d" % (showName, ep_obj.scene_season, ep_obj.scene_episode))
            strings.append("%s S%02d E%d" % (showName, ep_obj.scene_season, ep_obj.scene_episode))
            strings.append("%s S%d E%02d" % (showName, ep_obj.scene_season, ep_obj.scene_episode))
            strings.append("%s S%02dEp%02d" % (showName, ep_obj.scene_season, ep_obj.scene_episode))
            strings.append("%s S%02dEp%d" % (showName, ep_obj.scene_season, ep_obj.scene_episode))
            strings.append("%s S%dEp%02d" % (showName, ep_obj.scene_season, ep_obj.scene_episode))
            strings.append("%s S%02d Ep%02d" % (showName, ep_obj.scene_season, ep_obj.scene_episode))
            strings.append("%s S%02d Ep%d" % (showName, ep_obj.scene_season, ep_obj.scene_episode))
            strings.append("%s S%d Ep%02d" % (showName, ep_obj.scene_season, ep_obj.scene_episode))
            strings.append("%s S%02d Ep %02d" % (showName, ep_obj.scene_season, ep_obj.scene_episode))
            strings.append("%s S%02d Ep %d" % (showName, ep_obj.scene_season, ep_obj.scene_episode))
            strings.append("%s S%d Ep %02d" % (showName, ep_obj.scene_season, ep_obj.scene_episode))
        return strings

    def _get_title_and_url(self, item):
        cleanTitle = re.sub(r'(\s*\[[\w\s]+\-\w+\])',"",item.title)
        return cleanTitle, item.refererURL

    def getQuality(self, item):
        return item.quality

    def buildUrl(self, searchString, quality):
        if quality in self.qualityCategories:
            data = {'chkInit': '1', 'edTitre': searchString, 'chkTitre': 'on', 'chkFichier': 'on', 'chkCat': 'on',
                    'cats[]': self.qualityCategories[quality], 'edAge': '', 'edYear': ''}
        else:
            data = {'b_submit': 'BinnewZ', 'cats[]': 'all', 'edSearchAll': searchString, 'sections[]': 'all'}
        return data

    #wtf with the signature change...
    def _doSearch(self, searchString=None, show=None, season=None, french=None):
        if searchString is None:
            return []
        logger.log("BinNewz : Searching for " + searchString, logger.DEBUG)
        data = self.buildUrl(searchString.replace('!',''), show.quality)
        try:
            soup = BeautifulSoup(urllib2.urlopen("http://www.binnews.in/_bin/search2.php",
                                                 urllib.urlencode(data, True)))
        except Exception, e:
            logger.log(u"Error trying to load BinNewz response: " + e, logger.ERROR)
            return []

        results = []
        tables = soup.findAll("table", id="tabliste")
        for table in tables:
            if len(results)>5:
                break
            rows = table.findAll("tr")
            for row in rows:

                cells = row.select("> td")
                if len(cells) < 11:
                    continue

                name = cells[2].text.strip()
                language = cells[3].find("img").get("src")

                if show:
                    if show.audio_lang == "fr" or french:
                        if not "_fr" in language:
                            continue
                    elif show.audio_lang == "en":
                        if "_fr" in language:
                            continue

                # blacklist_groups = [ "alt.binaries.multimedia" ]
                blacklist_groups = []

                newgroupLink = cells[4].find("a")
                newsgroup = None
                if newgroupLink.contents:
                    newsgroup = newgroupLink.contents[0]
                    if newsgroup in self.allowedGroups:
                        newsgroup = self.allowedGroups[newsgroup]
                    else:
                        logger.log(u"Unknown binnewz newsgroup: " + newsgroup, logger.ERROR)
                        continue
                    if newsgroup in blacklist_groups:
                        logger.log(u"Ignoring result, newsgroup is blacklisted: " + newsgroup, logger.WARNING)
                        continue

                filename = cells[5].contents[0]
                
                acceptedQualities = Quality.splitQuality(show.quality)[0]
                quality = Quality.nameQuality(filename)
                if quality == Quality.UNKNOWN:
                    quality = self.getReleaseQuality(name)
                if quality not in acceptedQualities:
                    continue
                if filename in searchstringlist:
                    continue

                minSize = self.qualityMinSize[quality] if quality in self.qualityMinSize else 100
                searchItems = []
                #multiEpisodes = False

                rangeMatcher = re.search("(?i).*(?<![\s\.\-_])[\s\.\-_]+s?(?:aison)?[\s\.\-_]*\d{1,2}[\s\.\-_]?(?:x|dvd|[eéEÉ](?:p|pisodes?)?)[\s\.\-_]*(\d{1,2})(?:(?:[\s\.\-_]*(?:[aàAÀ,/\-\.\s\&_]|et|and|to|x)[\s\.\-_]*(?:x|dvd|[eéEÉ](?:p|pisodes?)?)?[\s\.\-_]*([0-9]{1,2})))+.*", name)
                if rangeMatcher:
                    rangeStart = int(rangeMatcher.group(1))
                    rangeEnd = int(rangeMatcher.group(2))
                    if filename.find("*") != -1:
                        for i in range(rangeStart, rangeEnd + 1):
                            searchItem = filename.replace("**", str(i))
                            searchItem = searchItem.replace("*", str(i))
                            searchItems.append(searchItem)
                    #else:
                    #    multiEpisodes = True

                if len(searchItems) == 0:
                    searchItems.append(filename)

                for searchItem in searchItems:
                    for downloader in self.nzbDownloaders:
                        searchstringlist.append(searchItem)
                        logger.log("Searching for download : " + name + ", search string = " + searchItem + " on " +
                                   downloader.__class__.__name__)
                        try:
                            binsearch_result = downloader.search(searchItem, minSize, newsgroup)
                            if binsearch_result:
                                links = []
                                if french:
                                    binsearch_result.audio_langs = 'fr'
                                else:
                                    binsearch_result.audio_langs = show.audio_lang
                                binsearch_result.title = searchString
                                binsearch_result.quality = quality
                                myDB = db.DBConnection()
                                listlink = myDB.select("SELECT link from episode_links where episode_id =?", [globepid])
                                for dlink in listlink:
                                    links.append(dlink[0])
                                if binsearch_result.nzburl in links:
                                    continue
                                else:
                                    results.append(binsearch_result)
                                    logger.log("Found : " + searchItem + " on " + downloader.__class__.__name__)
                                    break
                        except Exception, e:
                            logger.log("Searching from " + downloader.__class__.__name__ + " failed : " + str(e),
                                       logger.ERROR)

        return results

    def getResult(self, episodes):
        """
        Returns a result of the correct type for this provider
        """
        result = classes.NZBDataSearchResult(episodes)
        result.provider = self

        return result

    def getReleaseQuality(self, releaseName):
        name = releaseName.lower()
        checkName = lambda elemlist, func: func([re.search(x, name, re.I) for x in elemlist])

        if checkName(["dvdrip"], all):
            return Quality.SDDVD
        elif checkName(["720p", "hdtv"], all):
            return Quality.HDTV
        elif checkName(["1080p", "hdtv"], all):
            return Quality.FULLHDTV
        elif checkName(["720p", "webrip"], all):
            return Quality.HDWEBDL
        elif checkName(["1080p", "webrip"], all):
            return Quality.FULLHDWEBDL
        elif checkName(["720p", "blu ray"], all):
            return Quality.HDBLURAY
        elif checkName(["1080p", "blu ray"], all):
            return Quality.FULLHDBLURAY
        elif checkName(["dvdrip"], all):
            return Quality.SDDVD
        elif checkName(["tvrip"], all):
            return Quality.SDTV
        else:
            return Quality.SDTV


provider = BinNewzProvider()
