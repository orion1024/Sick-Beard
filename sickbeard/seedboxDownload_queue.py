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
import copy
import threading

import sickbeard
from sickbeard import db, logger, common, exceptions, helpers
from sickbeard import generic_queue
#from sickbeard import search
#from sickbeard import ui
import seedboxDownloadHelpers
from seedboxDownloadHelpers import print_bytes

class SeedboxDownloadQueue(generic_queue.GenericQueue):
    
    def __init__(self):
        generic_queue.GenericQueue.__init__(self)
        self.queue_name = "SEEDBOXDOWNLOADQUEUE"

    def is_in_queue(self, item):
        for cur_item in self.queue:
             if isinstance(cur_item, DownloadQueueItem) and cur_item.download.remote_file_path == item.download.remote_file_path:
                return True
        return False

    def pause_download(self, interrupt_cur_download=False, reason=""):
        self.min_priority = generic_queue.QueuePriorities.HIGH
        if interrupt_cur_download:
            self.currentItem.interrupt_download(reason)

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
            
    def run(self):

        # only start a new task if one isn't already going
        if self.thread == None or self.thread.isAlive() == False:

            # if the thread is dead then the current item should be finished
            if self.currentItem != None:
                
                self.currentItem.finish()
                
                # We add the item back into the queue if it failed.
                if self.currentItem.requeue_needed():
                    self.add_item(self.currentItem)
                    
                self.currentItem = None

            # if there's something in the queue then run it in a thread and take it out of the queue
            if len(self.queue) > 0:

                # sort by priority
                def sorter(x,y):
                    """
                    Sorts by priority descending then time ascending
                    """
                    if x.priority == y.priority:
                        if y.added == x.added:
                            return 0
                        elif y.added < x.added:
                            return 1
                        elif y.added > x.added:
                            return -1
                    else:
                        return y.priority-x.priority

                self.queue.sort(cmp=sorter)
                
                queueItem = self.queue[0]

                if queueItem.priority < self.min_priority:
                    return

                # launch the queue item in a thread
                # TODO: improve thread name
                threadName = self.queue_name + '-' + queueItem.get_thread_name()
                self.thread = threading.Thread(None, queueItem.execute, threadName)
                self.thread.start()

                self.currentItem = queueItem

                # take it out of the queue
                del self.queue[0]


class DownloadQueueItem(generic_queue.QueueItem):
    def __init__(self, download, protocol_wrapper_settings, remove_remote_on_success=False):
        generic_queue.QueueItem.__init__(self, 'Seedbox download')
        self.priority = generic_queue.QueuePriorities.NORMAL
       
        self.download = download
        self.remove_remote_on_success = remove_remote_on_success

        # We create a copy of the settings. this is to ensure download will use the current settings even if they are changed between now and the moment the download start.
        self.protocol_wrapper_settings = copy.deepcopy(protocol_wrapper_settings)
        
        # The protocol wrapper itself will be created just before the download starts.
        self.protocol_wrapper = None
        self.success = None

    def execute(self):
        generic_queue.QueueItem.execute(self)
        
        logger.log("Downloading from seedbox : %s" % self.download.Name, logger.DEBUG)
        
        self.success = False
        
        self.download.file_download_failed = False
        
        self.download.download_attempts = self.download.download_attempts + 1

        self.protocol_wrapper = seedboxDownloadHelpers.SeedboxDownloaderProtocolWrapper(self.protocol_wrapper_settings)
        
        if self.protocol_wrapper.connected:
            self.success = self.protocol_wrapper.get_file(self.download)
        else:
            self.success = False
            
        return

    # Interrupt the download
    def interrupt_download(self, reason=""):
        # This will cause the callback method to raise an exception the next time it gets called.
        if self.download.file_downloading:
            self.download.interrupt_asked = True
            self.download.interrupt_reason = reason
            
        return

    def finish(self):
        # don't let this linger if something goes wrong
        if self.success == None:
            self.success = False
        generic_queue.QueueItem.finish(self)
        
        logger.log("Finishing download from seedbox : %s with status %s" % (self.download.Name, self.success), logger.DEBUG)

        if self.remove_remote_on_success and self.success:
            logger.log("Now removing remote file from seedbox (full path : '%s') " % (self.download.remote_file_path), logger.DEBUG)
            try:                
                removeSuccessful = self.protocol_wrapper.delete_file(self.download.remote_file_path)
            except IOError as IOException:
                logger.log(u"Error when trying to remove remote file %s : %s" % (self.download.remote_file_path, str(IOException)), logger.DEBUG)
                return              
            except:
                logger.log(u"Unexpected error when trying to remove remote file %s. Exception : %s" % (self.download.remote_file_path, str(sys.exc_type)), logger.DEBUG)
                return
            else:
                if removeSuccessful:
                    logger.log("Remove completed successfully for file %s" % (self.download.remote_file_path), logger.DEBUG)
                    # We also try to remove the parent directories. They will be removed only if empty, and we stop at the remote root directory.
                    self.protocol_wrapper.delete_empty_dir(os.path.dirname(self.download.remote_file_path), recurse=True)
    
    # This method allows the queue to know if the item needs to be rescheduled.
    def requeue_needed(self):    
        return not self.success
    






      
