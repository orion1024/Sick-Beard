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
    def __init__(self, enabled=None, delete_remote_files=None, automove_in_postprocess_dir=None,
                    check_frequency=None, landing_dir=None, download_episodes_only=None,
                    protocol=None, sftp_remote_host=None, sftp_remote_port=22,
                    sftp_landing_dir=None, sftp_remote_root_dir=".", sftp_remote_user=None,
                    sftp_remote_auth_key=None, sftp_remote_password=None):
        
        self.enabled = enabled
        self.delete_remote_files = delete_remote_files
        self.automove_in_postprocess_dir = automove_in_postprocess_dir
        self.check_frequency = check_frequency
        self.landing_dir = landing_dir
        self.download_episodes_only = download_episodes_only

        self.protocol_settings = SeedboxDownloaderProtocolWrapperSettings(
                                            protocol, sftp_remote_host, sftp_remote_port,
                                            landing_dir, sftp_remote_root_dir,
                                            sftp_remote_user, sftp_remote_auth_key,
                                            sftp_remote_password)
                                                
        return
        
    def validate_settings(self):
        # TODO : to be coded
        
        result = True
        
        return result and self.protocol_settings.validate_settings()
        
        
# This class holds all settings related to the protocol wrapper.
# Kept separated from the general settings as it will passed on to the wrapper object and it doesn't care about general settings.
def SeedboxDownloaderProtocolWrapperSettings():

    def __init__(self,
                    protocol, sftp_remote_host=None, sftp_remote_port=22,
                    sftp_landing_dir=None, sftp_remote_root_dir=".", sftp_remote_user=None,
                    sftp_remote_auth_key=None, sftp_remote_password=None):

        self.protocol = protocol
        self.sftp_remote_host = sftp_remote_host
        self.sftp_remote_port = sftp_remote_port
        self.sftp_remote_user = sftp_remote_user
        self.sftp_remote_auth_key = sftp_remote_auth_key
        self.sftp_remote_password = sftp_remote_password
        self.sftp_remote_root_dir = sftp_remote_root_dir
        self.sftp_landing_dir = sftp_landing_dir
        
        return
        
    def validate_settings(self):
        # TODO : to be coded
        return True


# This class is meant to hold necessary information about a remote file to properly call the wrapper methods.
# The downloader will build these objects and supply them to the queue items so that the files get downloaded.
class SeedboxDownload():
    
    def __init__(self, remote_file_path, local_file_path, remoteName, file_size=0, file_already_present=False):

        self.remote_file_path = remote_file_path
        self.local_file_path= local_file_path
        self.file_size = file_size
        self.Name = remoteName
        self.file_already_present = file_already_present
        self.transferred_bytes = 0
        self.file_downloaded = False
        self.file_downloading = False
        
        # if the file download fails, this variable will be set to True
        self.file_download_failed = False
        # if the file download fails, this variable will be set to the exception message returned.
        self.file_download_error = ""

    
    # This method is meant to be passed to the wrapper as the callback method during transfers
    def update_download_progress(self, transferred_bytes, file_size):       
        self.file_size = file_size
        self.transferred_bytes = transferred_bytes
        return

    def __str__(self):
        return u"(remote_file_path="+str(self.remote_file_path)+";local_file_path="+str(self.local_file_path)+";file_size="+str(self.file_size)+";transferredSize="+str(self.transferred_bytes)+";file_downloaded="+str(self.file_downloaded)+")"
        
    def __repr__(self):
        return self.__str__()


# This class is meant to present common methods to use to download files, whatever transfer protocol is used.
# It is used by the seedbox downloader (to list the remote files to download and populate the queue with them) and the queue itself (to actually download said files)
# At first only SFTP will be supported, but it will make adding other protocols easier
class SeedboxDownloaderProtocolWrapper():
    
    def __init__(self, protocol, remote_host, remote_port, landingDir, remote_root_dir=".", remote_user=None, remote_auth_key=None, remote_password=None):

        self.protocol = protocol
        self.remote_host = remote_host
        self.remote_port = remote_port
        self.remote_user = remote_user
        self.remote_auth_key = remote_auth_key
        self.remote_password = remote_password
        self.remote_root_dir = remote_root_dir
        self.landingDir = landingDir

        # TODO : There should a logic to check the consistency of parameters AND the fact that we can actually connect.
        self.valid_configuration = True

        if self.protocol=="SFTP":
            self.sftp = pysftp.Connection(self.remote_host, self.remote_user, password=self.remote_password, log = True)

    # List all files in the given directory, and return a list of SeedBoxDownload objects. The files are tested for local existence in here too.
    def list_dir(self, remoteSubDir="", recursive=False, recursiveCall=False):
        results = []
        
       
        if self.protocol=="SFTP":
            
            # If this is not a recursive call (ie we were not called by list_dir but from another code), we prepend the root dir.
            # If it is a recursive call, it has already been done so no need to.
            # Simply checking for the presence of "remote_root_dir" in the parameter is not enough as the subdir could have the same name as the root dir, but we would still want to append it in that case.
            
            if recursiveCall:
                remoteDir = remoteSubDir
            else:
                if remoteSubDir != "":
                    remoteDir =  self.remote_root_dir + "/" + remoteSubDir
                else:
                    remoteDir =  self.remote_root_dir
            
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
                            #logger.log(u"Building local path... remote_root_dir = <" + str(self.remote_root_dir) + u">, remote_file_path = <" + str(remoteFullPath) + u">,landingDir = <" + str(self.landingDir)+u">", logger.DEBUG)
                            
                            local_file_path = os.path.normpath(self.landingDir + "/" + remoteFullPath.replace(re.escape(self.remote_root_dir)+ "/","",1))
                            #logger.log(u"LocalPath = <" + str(local_file_path) + u">", logger.DEBUG)
                            
                            results.append(SeedboxDownload(remoteFullPath, local_file_path, remote_filename, attr.st_size))
 
        return results

    def check_already_present_downloads(self, downloads):
        
        for download in downloads:
            download.file_already_present = self.is_file_downloaded(download.remote_file_path, download.local_file_path)
            
        return
    
    def get_file(self, download):
        
        if not self.valid_configuration:
            return False

        # Checking local conditions before starting the transfer.
        if self.is_file_downloaded(download.remote_file_path, download.local_file_path):
            download.file_already_present=True
            return False
        
        # if the file exists and is_file_downloaded returned False, this means a partial download.
        if os.path.exists(download.local_file_path):
            if self.protocol=="SFTP":
                # SFTP client doesn't handle resume so we need to remove the partially downloaded file
                try:
                    os.remove(download.local_file_path)
                except:
                    logger.log(u"Exception when trying to remove %s. Exception : %s" % (download.local_file_path, sys.exc_type), logger.DEBUG)
                    return False
            else:
                pass
        
        # If local directory does not exist we create it
        localDirectory = os.path.dirname(download.local_file_path)
        if not os.path.exists(localDirectory):
            try:
                os.makedirs(localDirectory)
            except:
                logger.log(u"Exception when trying to create local directory %s. Exception : %s" % (localDirectory, sys.exc_type), logger.DEBUG)
                return False
        
        # OK, now we can start downloading
        download.file_downloading = True
        download.file_download_failed = False
        try:
            self.sftp.get(download.remote_file_path, download.local_file_path, download.update_download_progress)
        except IOError as IOException:
            logger.log(u"Error when trying to get remote file %s : %s" % (download.remote_file_path, IOException), logger.DEBUG)
            download.file_download_failed = True
            download.file_download_error = str(IOException)
            download.file_downloaded = False
        else:
            download.file_downloaded = self.is_file_downloaded(download.remote_file_path, download.local_file_path)
        finally:
            download.file_downloading = False
        
        return download.file_downloaded

    def get_dir(self, remoteDir, recurse=False):
         # TODO : implement later. Same as get_file but for all files in specified directory

        return True

    def is_file_downloaded(self, remote_file_path, local_file_path):

        if os.path.exists(local_file_path):
            if self.protocol=="SFTP":
                return self.sftp.size_match(remote_file_path, local_file_path)
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

    def delete_file(self, remote_file_path):
        # TODO : implement later. Should return True or False whether the file deletion successfully completed or not
        
        if self.protocol=="SFTP":
            if self.sftp.exists(remote_file_path):
                self.sftp.remove(remote_file_path)
                return not self.sftp.exists(remote_file_path)
            else:
                return True
        else:
            pass
            
        return False

    # Returns False if directory is empty and remove attempt failed. Returns True otherwise (ie, if directory is not empty or it not a directory, nothing is done and method returns True
    def delete_empty_dir(self, remoteDir, recurse=False):
        
        if remoteDir == self.remote_root_dir:
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
