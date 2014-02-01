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
        self.downloads = []
        
        self.totalFiles = 0
        self.totalDownloadedFiles = 0
        self.totalAlreadyPresentFiles = 0
        self.totalFilesToDownload = 0
        self.totalDownloadedBytes = 0
        self.totalBytesToDownload = 0
        
        # temp until queue is implemented
        self.downloading = False


    def run(self):
        # TODO : implement later
        logger.log(u"Checking seedbox for files...", logger.MESSAGE)
        
        # temp until queue is implemented       
        if not self.downloading:
        
            self.downloading = True
            self.downloads = self.wrapper.list_dir(recursive=True)   
            
            logger.log(u"Got %d results. Computing stats..." % len(self.downloads), logger.MESSAGE)
            
            self.wrapper.check_already_present_downloads(self.downloads)
            self.update_download_stats()
            
            self.logDownloadStats()   

            # temp until queue is implemented
            
            if self.totalFilesToDownload > 0:    
                for download in self.downloads:
                    if not download.fileAlreadyPresent:
                        logger.log(u"Starting download for %s ..." % download.Name, logger.MESSAGE)
                        result = self.wrapper.get_file(download)
                        if download.fileDownloaded:
                            logger.log(u"%s successfully downloaded !" % download.Name, logger.MESSAGE)
                        else:
                            logger.log(u"%s not downloaded for some reason. Check your connection settings !" % download.Name, logger.MESSAGE)
                self.update_download_stats()                            
                self.logDownloadStats()
            else:
                logger.log(u"No files to download.", logger.MESSAGE)
                
            self.downloading = False
        
        return          

    # Computes stats about all downloads : total size, number of downloaded files, downloaded bytes until now...
    def update_download_stats(self):
        # TODO : implement later
        
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
        logger.log(u"Total files : %d (%d MB)" % (self.totalFiles,self.totalBytes/1024/1024), logger.MESSAGE)
        logger.log(u"Total downloaded files : %d (%d MB)" % (self.totalDownloadedFiles,self.totalDownloadedBytes/1024/1024), logger.MESSAGE)
        logger.log(u"Total files already present : %d (%d MB)" % (self.totalAlreadyPresentFiles,self.totalAlreadyPresentBytes/1024/1024), logger.MESSAGE)
        logger.log(u"Total files to download : %d (%d MB)" % (self.totalFilesToDownload,self.totalBytesToDownload/1024/1024), logger.MESSAGE)
        
        return 

# This class is meant to hold necessary information about a remote file to properly call the wrapper methods.
# The downloader will build these objects and supply them to the queue items so that the files get downloaded.
class SeedboxDownload():
    
    def __init__(self, remoteFilePath, localFilePath, remoteName, protocolWrapper, fileSize=0, fileAlreadyPresent=False):

        self.remoteFilePath = remoteFilePath
        self.localFilePath= localFilePath
        self.fileSize = fileSize
        self.Name = remoteName
        self.protocolWrapper = protocolWrapper
        self.fileAlreadyPresent = fileAlreadyPresent
        self.transferredBytes = 0
        self.fileDownloaded = False
        self.fileDownloading = False

    
    # This method is meant to be passed to the wrapper as the callback method during transfer
    def update_download_progress(self, transferredBytes, fileSize):       
        self.fileSize = fileSize
        self.transferredBytes = transferredBytes
        
        return

    def __str__(self):
        return u"(remoteFilePath="+str(self.remoteFilePath)+";localFilePath="+str(self.localFilePath)+";fileSize="+str(self.fileSize)+";transferredSize="+str(self.transferredBytes)+";fileDownloaded="+str(self.fileDownloaded)+")"
        
    def __repr__(self):
        return self.__str__()


# This class is meant to present common methods to use to download files, whatever transfer protocol is used.
# It is used by the seedbox downloader (to list the remote files to download and populate the queue with them) and the queue itself (to actually download said files)
# At first only SFTP will be supported, but it will make adding other protocols easier
class SeedboxDownloaderProtocolWrapper():
    
    def __init__(self, protocol, remoteHost, remotePort, landingDir, remoteRootDir="", remoteUser=None, remoteAuthKey=None, remotePassword=None):

        self.protocol = protocol
        self.remoteHost = remoteHost
        self.remotePort = remotePort
        self.remoteUser = remoteUser
        self.remoteAuthKey = remoteAuthKey
        self.remotePassword = remotePassword
        self.remoteRootDir = remoteRootDir
        self.landingDir = landingDir

        # TODO : There should a logic to check the consistency of parameters AND the fact that we can actually connect.
        self.validConfiguration = True

        if self.protocol=="SFTP":
            self.sftp = pysftp.Connection(self.remoteHost, self.remoteUser, password=self.remotePassword, log = True)

    # List all files in the given directory, and return a list of SeedBoxDownload objects. The files are tested for local existence in here too.
    def list_dir(self, remoteDir=".", recursive=False):
        results = []
        
        if self.protocol=="SFTP":
        
            remote_filenames = self.sftp.listdir(remoteDir)
            
            
            #logger.log(u"List dir results (raw) : " + str(remote_filenames), logger.DEBUG)
            
            for remote_filename in remote_filenames:
                remoteFullPath = remoteDir + "/" + remote_filename
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
                            
                    # Also checking that the file is a regular one.
                    elif stat.S_ISREG(attr.st_mode):
                        # Building local path out of the remote dir, the remote path and the landing directory.
                        
                        #logger.log(u"Stats retrieved : " + str(attr), logger.DEBUG)
                        #logger.log(u"Building local path... remoteRootDir = <" + str(self.remoteRootDir) + u">, remoteFilePath = <" + str(remoteFullPath) + u">,landingDir = <" + str(self.landingDir)+u">", logger.DEBUG)
                        
                        localFilePath = os.path.normpath(self.landingDir + "/" + remoteFullPath.replace(re.escape(self.remoteRootDir + "/"),"",1))
                        #logger.log(u"LocalPath = <" + str(localFilePath) + u">", logger.DEBUG)
                        
                        results.append(SeedboxDownload(remoteFullPath, localFilePath, remote_filename, self, attr.st_size))
 
        return results

    def check_already_present_downloads(self, downloads):
        
        for download in downloads:
            download.fileAlreadyPresent = self.is_file_downloaded(download.remoteFilePath, download.localFilePath)
            
        return
    
    def get_file(self, download):
        # TODO : implement later. Should return True or False whether download successfully completed or not.
        
        if not self.validConfiguration:
            return False

        # Checking local conditions before starting the transfer.
        if self.is_file_downloaded(download.remoteFilePath, download.localFilePath):
            download.fileAlreadyPresent=True
            return False
        
        # if the file exists and is_file_downloaded returned False, this means a partial download.
        if os.path.exists(download.localFilePath):
            if self.protocol=="SFTP":
                # SFTP client doesn't handle resume so we need to remove the partially downloaded file
                try:
                    os.remove(download.localFilePath)
                except:
                    logger.log(u"Exception when trying to remove %s. Exception : %s" % (download.localFilePath, IOexception), logger.DEBUG)
                    return False
            else:
                pass
        
        # If local directory does not exist we create it
        localDirectory = os.path.dirname(download.localFilePath)
        if not os.path.exists(localDirectory):
            try:
                os.makedirs(localDirectory)
            except:
                logger.log(u"Exception when trying to create local directory %s. Exception : %s" % (localDirectory, IOexception), logger.DEBUG)
                return False
        
        # OK, now we can start downloading
        download.fileDownloading = True
        self.sftp.get(download.remoteFilePath, download.localFilePath, download.update_download_progress)
        download.fileDownloading = False
        
        if self.is_file_downloaded(download.remoteFilePath, download.localFilePath):
            download.fileDownloaded = True
            return True
        else:
            download.fileDownloaded = False
            return False

        return False

    def get_dir(self, remoteDir, recurse=False):
         # TODO : implement later. Same as get_file but for all files in specified directory

        return True

    def is_file_downloaded(self, remoteFilePath, localFilePath):

        if os.path.exists(localFilePath):
            if self.protocol=="SFTP":
                return self.sftp.size_match(remoteFilePath, localFilePath)
            else:
                return False
        else:
            return False


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

# Helper method. Prints a value in Byte in a human readable way (ie 14 MG/GB whatever)
# Credits to Fred Cicera : http://stackoverflow.com/questions/1094841/reusable-library-to-get-human-readable-version-of-file-size
def printBytes(num):
    for x in ['bytes','KB','MB','GB']:
        if num < 1024.0 and num > -1024.0:
            return "%3.1f %s" % (num, x)
        num /= 1024.0
    return "%3.1f %s" % (num, 'TB')
