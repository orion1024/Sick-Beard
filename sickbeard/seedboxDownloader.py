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

import os.path
import stat
import sys
import re
import datetime

import sickbeard
from sickbeard import logger

from lib.pysftp import pysftp

import seedboxDownload_queue
import seedboxDownloadHelpers
from seedboxDownloadHelpers import printBytes

# This class will populate the download queue, primarily by using the protocol wrapper to list remote files to be downloaded.
class SeedboxDownloader():
    
    def __init__(self, *args):
    

        # TODO : implement getting settings from global sickbeard configuration
        
        #self.discoverProtocolWrapper = SeedboxDownloaderProtocolWrapper(*args)
        self.discoverProtocolWrapper = seedboxDownloadHelpers.SeedboxDownloaderProtocolWrapper("SFTP","localhost","",
                                                                "/home/orion1024/Documents/landing_dev", remoteRootDir="myremotedir",
                                                                remoteUser="sftp", remotePassword="p59kN85vTaqnkGoEJsgt")
        # TODO : for the moment we use a wrapper for the queue. It isn't ideal if this one hangs. Should I just create a new wrapper when each file is downloading ?
        # maybe pass on a wrapper setting object that allows the download object to rebuild a wrapper when its current one fails. Food for thought !
        self.queueProtocolWrapper = seedboxDownloadHelpers.SeedboxDownloaderProtocolWrapper("SFTP","localhost","",
                                                                "/home/orion1024/Documents/landing_dev", remoteRootDir="myremotedir",
                                                                remoteUser="sftp", remotePassword="p59kN85vTaqnkGoEJsgt")
        self.removeRemoteFilesOnSuccess = False 
        

        self.downloads = []
        self.downloadQueue = seedboxDownload_queue.SeedboxDownloadQueue()
        
        # Initializing stats variables
        self.totalFiles = 0
        self.totalDownloadedFiles = 0
        self.totalAlreadyPresentFiles = 0
        self.totalFilesToDownload = 0
        self.totalDownloadedBytes = 0
        self.totalBytesToDownload = 0
        

    def run(self):
        logger.log(u"Checking seedbox for files...", logger.MESSAGE)
           
        newDownloads = self.discoverProtocolWrapper.list_dir(self.queueProtocolWrapper, recursive=True)   
        
        logger.log(u"Got %d results. Computing stats..." % len(newDownloads), logger.MESSAGE)
        
        self.discoverProtocolWrapper.check_already_present_downloads(newDownloads)
       
        # TODO : remove this line later when testing is over.
        self.downloads = []
        
        self.addNewDownloads(newDownloads)
        
        self.update_download_stats()
        self.logDownloadStats()
    
        return          

    # Add new downloads if it isn't already in the list, to the internal list AND to the queue.
    def addNewDownloads(self, newDownloads):
        
        newDownloadCount = 0
        for newDownload in newDownloads:
            if not self.isDownloadKnown(newDownload):
                self.downloads.append(newDownload)
                if not newDownload.fileAlreadyPresent:
                    self.downloadQueue.add_item(seedboxDownload_queue.DownloadQueueItem(newDownload, self.removeRemoteFilesOnSuccess))
                    newDownloadCount += 1
                    
        logger.log(u"%d new files to download." % newDownloadCount, logger.MESSAGE)
        return

    # Returns True if the download object given already exists in the list of downloads.
    def isDownloadKnown(self, newDownload):
    
        for download in self.downloads:
            if download.remoteFilePath == newDownload.remoteFilePath:
                return True
        
        return False

        
    # Computes stats about all downloads : total size, number of downloaded files, downloaded bytes until now...
    def update_download_stats(self):
        
        self.totalFiles = 0
        self.totalBytes = 0
        self.totalDownloadedFiles = 0
        self.totalDownloadedBytes = 0
        self.totalAlreadyPresentFiles = 0
        self.totalAlreadyPresentBytes = 0
        self.totalFilesToDownload = 0
        self.totalBytesToDownload = 0

        
        for download in self.downloads:
            self.totalFiles += 1
            self.totalBytes += download.fileSize
 
            # A file is either downloaded (implicitely in this session), already present (previously downloaded), or in the queue          
            if download.fileDownloaded:
                self.totalDownloadedFiles += 1
                self.totalDownloadedBytes += download.fileSize
            elif download.fileAlreadyPresent:
                self.totalAlreadyPresentFiles += 1
                self.totalAlreadyPresentBytes += download.fileSize  
            else:
                self.totalFilesToDownload += 1
                # If file is currently downloading, we take the transferredBytes into account
                if download.fileDownloading:
                    self.totalBytesToDownload += download.fileSize - download.transferredBytes
                    self.totalDownloadedBytes += download.transferredBytes
                else:
                    self.totalBytesToDownload += download.fileSize   
        
        return

    # Logs stats to Sickbeard log file : total size, number of downloaded files, downloaded bytes until now...
    def logDownloadStats(self):
        # TODO : complete later
        logger.log(u"Total files : %d (%s)" % (self.totalFiles,printBytes(self.totalBytes)), logger.MESSAGE)
        logger.log(u"Total downloaded files : %d (%s)" % (self.totalDownloadedFiles,printBytes(self.totalDownloadedBytes)), logger.MESSAGE)
        logger.log(u"Total files already present : %d (%s)" % (self.totalAlreadyPresentFiles,printBytes(self.totalAlreadyPresentBytes)), logger.MESSAGE)
        logger.log(u"Total files to download : %d (%s)" % (self.totalFilesToDownload,printBytes(self.totalBytesToDownload)), logger.MESSAGE)
        logger.log(u"Total files in download queue : %d" % (len(self.downloadQueue.queue)), logger.MESSAGE)

        
        return 

