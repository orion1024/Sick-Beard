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

import sickbeard
from lib.pysftp import pysftp

from sickbeard import logger

# This class will populate the download queue, primarily by using the protocol wrapper to list remote files to be downloaded.
class SeedboxDownloader():
    
    def __init__(self, *args):
        # TODO : implement later

        #self.wrapper = SeedboxDownloaderProtocolWrapper(*args)
        self.wrapper = SeedboxDownloaderProtocolWrapper("SFTP","localhost","","/home/orion1024/Documents/landing_dev",remoteUser="sftp", remotePassword="p59kN85vTaqnkGoEJsgt")
        


    def run(self):
        # TODO : implement later
        logger.log(u"Checking seedbox for files...", logger.MESSAGE)
        
        downloads = self.wrapper.list_dir(recursive=True)   
        
        logger.log(u"Got %d results :" % len(downloads), logger.DEBUG)
        for download in downloads:
            logger.log(str(download), logger.DEBUG)


# This class is meant to hold necessary information about a remote file to properly call the wrapper methods.
# The downloader will build these objects and supply them to the queue items so that the files get downloaded.
class SeedboxDownload():
    
    def __init__(self, remoteFilePath, localFilePath, fileSize=0):
        # TODO : implement later
        self.remoteFilePath = remoteFilePath
        self.localFilePath= localFilePath
        self.fileSize = fileSize
        self.transferredBytes = 0
        self.fileChecked = False
    
    # This method is meant to be passed as the callback method during transfer
    def updateDownloadProgress(transferredBytes, fileSize):
        self.fileSize = fileSize
        self.transferredBytes = transferredBytes

    def __str__(self):
        return u"(remoteFilePath="+str(self.remoteFilePath)+";localFilePath="+str(self.localFilePath)+";fileSize="+str(self.fileSize)+";transferredSize="+str(self.transferredBytes)+";fileChecked="+str(self.fileChecked)+")"
        
    def __repr__(self):
        return self.__str__()


# This class is meant to present common methods to use to download files, whatever transfer protocol is used.
# It is used by the seedbox downloader (to list the remote files to download and populate the queue with them) and the queue itself (to actually download said files)
# At first only SFTP will be supported, but it will make adding other protocols easier
class SeedboxDownloaderProtocolWrapper():
    
    def __init__(self, protocol, remoteHost, remotePort, landingDir, remoteRootDir="", remoteUser=None, remoteAuthKey=None, remotePassword=None):
        # TODO : implement later. There should be a logic to check the consistency of parameters.
        self.protocol = protocol
        self.remoteHost = remoteHost
        self.remotePort = remotePort
        self.remoteUser = remoteUser
        self.remoteAuthKey = remoteAuthKey
        self.remotePassword = remotePassword
        self.remoteRootDir = remoteRootDir
        self.landingDir = landingDir

        # TODO : There should a logic to check the consistency of parameters.
        self.validConfiguration = True

        if self.protocol=="SFTP":
            self.sftp = pysftp.Connection(self.remoteHost, self.remoteUser, password=self.remotePassword, log = True)



    def list_dir(self, remoteDir=".", recursive=False):
        # TODO : implement later
        results = []
        
        remote_filepaths = self.sftp.listdir(remoteDir)
        
        
        logger.log(u"List dir results (raw) : " + str(remote_filepaths), logger.DEBUG)
        
        for remote_filepath in remote_filepaths:
            remoteFullPath = remoteDir + "/" + remote_filepath
            #logger.log(u"Getting stats for file " + str(remoteFullPath), logger.DEBUG)
            
            try:
                attr = self.sftp.stat(remoteFullPath)
            except IOError as IOexception:
                logger.log(u"IO error: %s" % IOexception, logger.DEBUG)
            else:
                # Directories are not listed themselves, but we do explore them if a recursive listing has been asked.
                if stat.S_ISDIR(attr.st_mode):
                    if recursive:
                        results.extend(self.list_dir(remoteFullPath, True))
                else:
                    # Building local path out of the remote dir, the remote path and the landing directory.
                    
                    #logger.log(u"Stats retrieved : " + str(attr), logger.DEBUG)
                    #logger.log(u"Building local path... remoteRootDir = <" + str(self.remoteRootDir) + u">, remoteFilePath = <" + str(remoteFullPath) + u">,landingDir = <" + str(self.landingDir)+u">", logger.DEBUG)
                    
                    localFilePath = os.path.normpath(self.landingDir + "/" + remoteFullPath.replace(re.escape(self.remoteRootDir + "/"),"",1))
                    #logger.log(u"LocalPath = <" + str(localFilePath) + u">", logger.DEBUG)
                    results.append(SeedboxDownload(remoteFullPath, localFilePath, attr.st_size))
 
        return results

    def get_file(self, download_obj):
        # TODO : implement later. Should return True or False whether download successfully completed or not
        
        # Building
        #if os.path.exists(

        return True

    def get_dir(self, remoteDir, recurse=False):
         # TODO : implement later. Same as get_file but for all files in specified directory

        return True

    def is_file_downloaded(self, download_obj):
        # TODO : implement later. Should return True or False whether the file is present locally, and with the same size as the remote version.

        return True

    def is_dir_downloaded(self, remoteDir, recurse=False):
        # TODO : implement later. Same as is_file_downloaded but for all files in specified directory

        return True

    def delete_file(self, remoteDir, fileName):
        # TODO : implement later. Should return True or False whether the file deletion successfully completed or not

        return True

    def delete_dir(self, remoteDir, recurse=False):
        # TODO : implement later. Same as delete_file but for all files in specified directory
         
        return True

    def connect(self):
        # TODO : implement later. This function should be called only internally if necessary, not by outside code. Objective is to keep the internal workings hidden from calling objects.
        return True

    def disconnect(self):
        # TODO : implement later. This function should be called only internally if necessary,, not by outside code. Objective is to keep the internal workings hidden from calling objects.
        return True

