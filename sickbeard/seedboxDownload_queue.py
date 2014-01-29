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


class SeedboxDownloadQueue(generic_queue.GenericQueue):
    
    def __init__(self):
        generic_queue.GenericQueue.__init__(self)
        self.queue_name = "SEEDBOXDOWNLOADQUEUE"

    def is_in_queue(self, download):
        # TODO : implement later
        # for cur_item in self.queue:
        #     if isinstance(cur_item, DownloadQueueItem) and cur_item.show == show and cur_item.segment == segment:
        #        return True
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
        if isinstance(item, BacklogQueueItem) and not self.is_in_queue(item):
            generic_queue.GenericQueue.add_item(self, item)
        else:
            logger.log(u"Not adding item, it's already in the queue", logger.DEBUG)

class DownloadQueueItem(generic_queue.QueueItem):
    def __init__(self, download_obj):
        generic_queue.QueueItem.__init__(self, 'Seedbox download', MANUAL_SEARCH)
        self.priority = generic_queue.QueuePriorities.NORMAL

        # TODO : implement later        
        self.download_obj = download_obj
     
        self.success = None

    def execute(self):
        generic_queue.QueueItem.execute(self)

        # TODO : implement later
        logger.log("Downloading from seedbox : " + self.download_obj.Name)


        self.success = result

    def finish(self):
        # TODO : implement later
        # don't let this linger if something goes wrong
        if self.success == None:
            self.success = False
        generic_queue.QueueItem.finish(self)

