# Author: Ludovic SARAKHA
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
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Sick Beard.  If not, see <http://www.gnu.org/licenses/>.

import datetime
import operator

import sickbeard

from sickbeard import db
from sickbeard import helpers, logger, show_name_helpers
from sickbeard import providers
from sickbeard import search
from sickbeard.common import SNATCHED_FRENCH

from name_parser.parser import NameParser, InvalidNameException


class FrenchFinder():

    def __init__(self, force=None, show=None):

        #TODOif not sickbeard.DOWNLOAD_FRENCH:
        #    return
        if sickbeard.showList==None:
            return
        logger.log(u"Beginning the search for french episodes older than "+ str(sickbeard.FRENCH_DELAY) +" days")
       
        frenchlist=[]
        #get list of english episodes that we want to search in french
        myDB = db.DBConnection()
        today = datetime.date.today().toordinal()
        if show:
            frenchsql=myDB.select("SELECT showid, season, episode from tv_episodes where audio_langs='en' and tv_episodes.showid =? and (? - tv_episodes.airdate) > ? order by showid, airdate asc",[show,today,sickbeard.FRENCH_DELAY]) 
            count=myDB.select("SELECT count(*) from tv_episodes where audio_langs='en' and tv_episodes.showid =? and (? - tv_episodes.airdate) > ?",[show,today,sickbeard.FRENCH_DELAY]) 
        else:
            frenchsql=myDB.select("SELECT showid, season, episode from tv_episodes, tv_shows where audio_langs='en' and tv_episodes.showid = tv_shows.tvdb_id and tv_shows.frenchsearch = 1 and (? - tv_episodes.airdate) > ? order by showid, airdate asc",[today,sickbeard.FRENCH_DELAY])
            count=myDB.select("SELECT count(*) from tv_episodes, tv_shows where audio_langs='en' and tv_episodes.showid = tv_shows.tvdb_id and tv_shows.frenchsearch = 1 and (? - tv_episodes.airdate) > ?",[today,sickbeard.FRENCH_DELAY])
        #make the episodes objects
        logger.log(u"Searching for "+str(count[0][0]) +" episodes in french")
        for episode in frenchsql:
            showObj = helpers.findCertainShow(sickbeard.showList, episode[0])
            epObj = showObj.getEpisode(episode[1], episode[2])
            frenchlist.append(epObj)
        
        #for each episode in frenchlist fire a search in french
        delay=[]
        for frepisode in frenchlist:
            if frepisode.show.tvdbid in delay:
                logger.log(u"Previous episode for show "+str(frepisode.show.tvdbid)+" not found in french so skipping this search", logger.DEBUG)
                continue
            result=[]
            for curProvider in providers.sortedProviderList():

                if not curProvider.isActive():
                    continue

                logger.log(u"Searching for french episodes on "+curProvider.name +" for " +frepisode.show.name +" season "+str(frepisode.season)+" episode "+str(frepisode.episode))
                try:
                    curfrench = curProvider.findFrench(frepisode, manualSearch=True)
                except:
                    logger.log(u"Exception", logger.DEBUG)
                    pass
                if curfrench:
                    for x in curfrench:
                        if not show_name_helpers.filterBadReleases(x.name):
                            logger.log(u"French "+x.name+" isn't a valid scene release that we want, ignoring it", logger.DEBUG)
                            continue
                        result.append(x)
            best=None
            try:
                epi={}
                epi[1]=frepisode
                best = search.pickBestResult(result, episode = epi)
            except:
                pass
            if best:
                best.name=best.name + ' snatchedfr'
                logger.log(u"Found french episode for " +frepisode.show.name +" season "+str(frepisode.season)+" episode "+str(frepisode.episode))
                try:
                    search.snatchEpisode(best, SNATCHED_FRENCH)
                except:
                    logger.log(u"Exception", logger.DEBUG)
                    pass
            else:
                delay.append(frepisode.show.tvdbid)
                logger.log(u"No french episodes found for " +frepisode.show.name +" season "+str(frepisode.season)+" episode "+str(frepisode.episode))
        