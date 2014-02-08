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

# This class holds all settings related to the module. Whether it's enabled, to delete remote files, etc.
# All general settings are kept as properties, all protocol-specific settings are kept as an object of type SeedboxDownloaderProtocolWrapperSettings
# This allows to pass a setting object to the wrapper, without giving it all settings.
def SeedboxDownloaderSettings():
    def __init__(self, seedboxdownload_enabled = None, seedboxdownload_delete_remote_files = None, seedboxdownload_automove_in_postprocess_dir = None,
                                    seedboxdownload_check_frequency = None, seedboxdownload_landing_dir = None, seedboxdownload_download_episodes_only = None):
        # TODO : to be implemented
        
        
        self.protocolSettings = SeedboxDownloaderProtocolWrapperSettings()
    
        return
        
# This class holds all settings related to the protocol wrapper. Kept separated from 
def SeedboxDownloaderProtocolWrapperSettings():
    def __init__(self):
        # TODO : to be implemented
    
        return
        


# This class is meant to hold necessary information about a remote file to properly call the wrapper methods.
# The downloader will build these objects and supply them to the queue items so that the files get downloaded.
class SeedboxDownload():
    
    def __init__(self, remoteFilePath, localFilePath, remoteName, fileSize=0, fileAlreadyPresent=False):

        self.remoteFilePath = remoteFilePath
        self.localFilePath= localFilePath
        self.fileSize = fileSize
        self.Name = remoteName
        self.fileAlreadyPresent = fileAlreadyPresent
        self.transferredBytes = 0
        self.fileDownloaded = False
        self.fileDownloading = False
        
        # if the file download fails, this variable will be set to True
        self.fileDownloadFailed = False
        # if the file download fails, this variable will be set to the exception message returned.
        self.fileDownloadError = ""

    
    # This method is meant to be passed to the wrapper as the callback method during transfers
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
    
    def __init__(self, protocol, remoteHost, remotePort, landingDir, remoteRootDir=".", remoteUser=None, remoteAuthKey=None, remotePassword=None):

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
    def list_dir(self, remoteSubDir="", recursive=False, recursiveCall=False):
        results = []
        
       
        if self.protocol=="SFTP":
            
            # If this is not a recursive call (ie we were not called by list_dir but from another code), we prepend the root dir.
            # If it is a recursive call, it has already been done so no need to.
            # Simply checking for the presence of "remoteRootDir" in the parameter is not enough as the subdir could have the same name as the root dir, but we would still want to append it in that case.
            
            if recursiveCall:
                remoteDir = remoteSubDir
            else:
                if remoteSubDir != "":
                    remoteDir =  self.remoteRootDir + "/" + remoteSubDir
                else:
                    remoteDir =  self.remoteRootDir
            
            #logger.log(u"Getting content of remote directory %s ..." % remoteDir, logger.DEBUG)
            try:
                remote_filenames = self.sftp.listdir(remoteDir)
            except IOError as IOexception:
                logger.log(u"Error while listing directory %s (%s)" % (remoteDir, IOexception), logger.DEBUG)
            else:
            
                #logger.log(u"List dir results (raw) : " + str(remote_filenames), logger.DEBUG)
                
                for remote_filename in remote_filenames:
                    remoteFullPath = remoteDir + "/" + remote_filename
                    #logger.log(u"Getting stats for file " + str(remoteFullPath), logger.DEBUG)
                    
                    try:
                        attr = self.sftp.stat(remoteFullPath)
                    except IOError as IOexception:
                        logger.log(u"Error while getting file info for %s (%s)" % (remoteFullPath, IOexception), logger.DEBUG)
                    else:
                        # Directories are not listed themselves, but we do explore them if a recursive listing has been asked.
                        if stat.S_ISDIR(attr.st_mode):
                            if recursive:
                                results.extend(self.list_dir(remoteFullPath, True, True))
                                
                        # Also checking that the file is a regular one.
                        elif stat.S_ISREG(attr.st_mode):
                            # Building local path out of the remote dir, the remote path and the landing directory.
                            
                            #logger.log(u"Stats retrieved : " + str(attr), logger.DEBUG)
                            #logger.log(u"Building local path... remoteRootDir = <" + str(self.remoteRootDir) + u">, remoteFilePath = <" + str(remoteFullPath) + u">,landingDir = <" + str(self.landingDir)+u">", logger.DEBUG)
                            
                            localFilePath = os.path.normpath(self.landingDir + "/" + remoteFullPath.replace(re.escape(self.remoteRootDir)+ "/","",1))
                            #logger.log(u"LocalPath = <" + str(localFilePath) + u">", logger.DEBUG)
                            
                            results.append(SeedboxDownload(remoteFullPath, localFilePath, remote_filename, attr.st_size))
 
        return results

    def check_already_present_downloads(self, downloads):
        
        for download in downloads:
            download.fileAlreadyPresent = self.is_file_downloaded(download.remoteFilePath, download.localFilePath)
            
        return
    
    def get_file(self, download):
        
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
                    logger.log(u"Exception when trying to remove %s. Exception : %s" % (download.localFilePath, sys.exc_type), logger.DEBUG)
                    return False
            else:
                pass
        
        # If local directory does not exist we create it
        localDirectory = os.path.dirname(download.localFilePath)
        if not os.path.exists(localDirectory):
            try:
                os.makedirs(localDirectory)
            except:
                logger.log(u"Exception when trying to create local directory %s. Exception : %s" % (localDirectory, sys.exc_type), logger.DEBUG)
                return False
        
        # OK, now we can start downloading
        download.fileDownloading = True
        download.fileDownloadFailed = False
        try:
            self.sftp.get(download.remoteFilePath, download.localFilePath, download.update_download_progress)
        except IOError as IOException:
            logger.log(u"Error when trying to get remote file %s : %s" % (download.remoteFilePath, IOException), logger.DEBUG)
            download.fileDownloadFailed = True
            download.fileDownloadError = str(IOException)
            download.fileDownloaded = False
        else:
            download.fileDownloaded = self.is_file_downloaded(download.remoteFilePath, download.localFilePath)
        finally:
            download.fileDownloading = False
        
        return download.fileDownloaded

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

    # Tries to reset the connection. Usually called when an error occurred during a normal operation.
    def reset(self):
        if self.protocol=="SFTP":
            self.sftp._sftp_connect()
        else:
            pass

    def is_dir_downloaded(self, remoteDir, recurse=False):
        # TODO : implement later. Same as is_file_downloaded but for all files in specified directory

        return True

    def delete_file(self, remoteFilePath):
        # TODO : implement later. Should return True or False whether the file deletion successfully completed or not
        
        if self.protocol=="SFTP":
            if self.sftp.exists(remoteFilePath):
                self.sftp.remove(remoteFilePath)
                return not self.sftp.exists(remoteFilePath)
            else:
                return True
        else:
            pass
            
        return False

    # Returns False if directory is empty and remove attempt failed. Returns True otherwise (ie, if directory is not empty or it not a directory, nothing is done and method returns True
    def delete_empty_dir(self, remoteDir, recurse=False):
        
        if remoteDir == self.remoteRootDir:
            logger.log("Not removing %s since it is the configured remote root directory." % remoteDir, logger.DEBUG)
            return True
        else:
            try:
                if self.sftp.exists(remoteDir):
                    attr = self.sftp.stat(remoteDir)
                    if stat.S_ISDIR(attr.st_mode):
                        fileList = self.sftp.listdir(remoteDir)
                        if len(fileList) == 0:
                            logger.log("Removing remote empty directory %s" % remoteDir, logger.DEBUG)
                            self.sftp.rmdir(remoteDir)
                            
                            # If the remove was successful and this is a recursive remove, we now try to remove the parent directory.
                            if not self.sftp.exists(remoteDir):
                                if recurse:
                                    return self.delete_empty_dir(os.path.dirname(remoteDir), True)
                                else:
                                    return True 
                            else:
                                return False
                        else:
                            logger.log("Remote directory %s not empty : %d file(s) found." % (remoteDir, len(fileList)), logger.DEBUG)
                            return False
                    else:
                        logger.log("%s is not a directory. Not removing it." % (remoteDir), logger.DEBUG)
                        return False
                else:
                    return False
            except IOError as IOException:
                logger.log(u"Error when trying to remove remote directory %s : %s" % (remoteDir, str(IOException)), logger.DEBUG)
                return False           
            except:
                logger.log(u"Unexpected error when trying to remove remote directory %s. Exception : %s" % (remoteDir, str(sys.exc_type)), logger.DEBUG)
                return False


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
