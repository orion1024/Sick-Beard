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
import sys
import os

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
        for cur_item in self.queue:
             if isinstance(cur_item, DownloadQueueItem) and cur_item.download.remoteFilePath == item.download.remoteFilePath:
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
        # don't do duplicates
        if isinstance(item, DownloadQueueItem) and not self.is_in_queue(item):
            generic_queue.GenericQueue.add_item(self, item)
        else:
            logger.log(u"Not adding item, it's already in the queue or not the right type of object.", logger.DEBUG)

class DownloadQueueItem(generic_queue.QueueItem):
    def __init__(self, download, protocolWrapper, removeRemoteOnSuccess=False):
        generic_queue.QueueItem.__init__(self, 'Seedbox download')
        self.priority = generic_queue.QueuePriorities.NORMAL
       
        self.download = download
        self.protocolWrapper = protocolWrapper
        self.removeRemoteOnSuccess = removeRemoteOnSuccess
     
        self.success = None

    def execute(self):
        generic_queue.QueueItem.execute(self)
        
        logger.log("Downloading from seedbox : %s" % self.download.Name, logger.DEBUG)
        
        self.success = None
        
        self.download.fileDownloadFailed = False
        
        self.success = self.protocolWrapper.get_file(self.download)


    def finish(self):
        # don't let this linger if something goes wrong
        if self.success == None:
            self.success = False
        generic_queue.QueueItem.finish(self)
        
        logger.log("Finishing download from seedbox : %s with status %s" % (self.download.Name, self.success), logger.DEBUG)
        
        # TODO : move the file to sickbeard post process directory if transfer is a success
        # TODO NEXT : remove remote directory if empty. Here or somewhere else ?
     
        if self.removeRemoteOnSuccess and self.success:
            logger.log("Now removing remote file from seedbox (full path : '%s') " % (self.download.remoteFilePath), logger.DEBUG)
            try:                
                removeSuccessful = self.protocolWrapper.delete_file(self.download.remoteFilePath)
            except IOError as IOException:
                logger.log(u"Error when trying to remove remote file %s : %s" % (self.download.remoteFilePath, str(IOException)), logger.DEBUG)
                return              
            except:
                logger.log(u"Unexpected error when trying to remove remote file %s. Exception : %s" % (self.download.remoteFilePath, str(sys.exc_type)), logger.DEBUG)
                return
            else:
                if removeSuccessful:
                    logger.log("Remove completed successfully for file %s" % (self.download.remoteFilePath), logger.DEBUG)
                    # We also try to remove the parent directories. They will be removed only if empty, and we stop at the remote root directory.
                    self.protocolWrapper.delete_empty_dir(os.path.dirname(self.download.remoteFilePath), recurse=True)  






      
