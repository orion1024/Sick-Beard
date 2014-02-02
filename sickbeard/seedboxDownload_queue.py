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
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Sick Beard.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import with_statement

import datetime
import time

import sickbeard
from sickbeard import db, logger, common, exceptions, helpers
from sickbeard import generic_queue
#from sickbeard import search
#from sickbeard import ui
import seedboxDownloadHelpers
from seedboxDownloadHelpers import printBytes

class SeedboxDownloadQueue(generic_queue.GenericQueue):
    
    def __init__(self):
        generic_queue.GenericQueue.__init__(self)
        self.queue_name = "SEEDBOXDOWNLOADQUEUE"

    def is_in_queue(self, item):
        # TODO : implement later
        for cur_item in self.queue:
             if isinstance(cur_item, DownloadQueueItem) and cur_item.download_obj.Name == item.download_obj.Name:
                return True
        return False

    def pause_download(self):
        self.min_priority = generic_queue.QueuePriorities.HIGH

    def unpause_download(self):
        self.min_priority = 0

    def is_download_paused(self):
        # backlog priorities are NORMAL, this should be done properly somewhere
        return self.min_priority >= generic_queue.QueuePriorities.NORMAL

    def is_download_in_progress(self):
        for cur_item in self.queue + [self.currentItem]:
            if isinstance(cur_item, DownloadQueueItem):
                return True
        return False

    def add_item(self, item):
        # TODO : implement later
        # don't do duplicates
        if isinstance(item, DownloadQueueItem) and not self.is_in_queue(item):
            generic_queue.GenericQueue.add_item(self, item)
        else:
            logger.log(u"Not adding item, it's already in the queue or not the right type of object.", logger.DEBUG)

class DownloadQueueItem(generic_queue.QueueItem):
    def __init__(self, download_obj, removeRemoteOnSuccess=False):
        generic_queue.QueueItem.__init__(self, 'Seedbox download')
        self.priority = generic_queue.QueuePriorities.NORMAL
       
        self.download_obj = download_obj
        self.removeRemoteOnSuccess = removeRemoteOnSuccess
     
        self.success = None

    def execute(self):
        generic_queue.QueueItem.execute(self)

        # TODO : implement later
        logger.log("Downloading from seedbox : %s" % self.download_obj.Name, logger.DEBUG)
        
        self.success = None
        self.success = self.download_obj.download()


    def finish(self):
        # don't let this linger if something goes wrong
        if self.success == None:
            self.success = False
        generic_queue.QueueItem.finish(self)
        
        logger.log("Finishing download from seedbox : %s with status %s" % (self.download_obj.Name, self.success), logger.DEBUG)
        
        # TODO : logic to move the file to sickbeard post process directory if transfer is a success
        # TODO : logic to remove remote file if this is the configuration
        
        if self.removeRemoteOnSuccess and self.success:
            logger.log("Now removing remote file from seedbox (full path : '%s') " % (self.download_obj.remoteFilePath), logger.DEBUG)
            try:
                if download_obj.removeRemoteVersion():
                    logger.log("Remove completed successfully for file %s" % (self.download_obj.remoteFilePath), logger.DEBUG)
            except:
                logger.log(u"Exception when trying to remove remote file %s. Exception : %s" % (self.download_obj.remoteFilePath, IOexception), logger.DEBUG)
                return False






      
