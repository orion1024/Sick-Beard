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

import sickbeard
from lib.pysftp import pysftp

from sickbeard import logger

# This class will populate the download queue, primarily by using the protocol wrapper to list remote files to be downloaded.
class SeedboxDownloader():
    
    def __init__(self, *args):
        # TODO : implement later

        #self.wrapper = SeedboxDownloaderProtocolWrapper(*args)
        self.wrapper = SeedboxDownloaderProtocolWrapper("","","","","")
        


    def run(self):
        # TODO : implement later
        logger.log(u"Checking seedbox for files...", logger.MESSAGE)
        
        list_result = self.wrapper.list_dir()
        logger.log(u"List dir results : " + str(list_result), logger.DEBUG)

# This class is meant to hold necessary information to properly call the wrapper methods.
# The downloader will build these objects and supply them to the queue items so that the files get downloaded.
class SeedboxDownload():
    
    def __init__(self, filePath, fileSize=0):
        # TODO : implement later
        self.filePath = filePath
        self.fileSize = fileSize
        self.transferredSize = 0
        self.fileChecked = False

    def __str__(self):
        return u"(filePath="+str(self.filePath)+";fileSize="+str(self.fileSize)+";transferredSize="+str(self.transferredSize)+";fileChecked="+str(self.fileChecked)+")"
        
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

        #if self.protocol=="SFTP"
            #self.SFTPConnection = pysftp.Connection(remoteHost, remoteUser, remoteAuthKey, remotePassword, remotePort, log = True)
        self.sftp = pysftp.Connection("localhost", "sftp", password="p59kN85vTaqnkGoEJsgt", log = True)



    def list_dir(self, remoteDir="", recursive=False):
        # TODO : implement later
        results = []
        
        remote_filenames = self.sftp.listdir()
        
        
        logger.log(u"List dir results (raw) : " + str(remote_filenames), logger.DEBUG)
        
        for remote_filename in remote_filenames:
            logger.log(u"Getting stats for file " + str(remote_filename), logger.DEBUG)
            attr = self.sftp.stat(remote_filename)
            logger.log(u"Stats retrieved : " + str(attr), logger.DEBUG)
            results.append(SeedboxDownload(remote_filename, attr.st_size))
        
        return results

    def get_file(self, remoteDir, fileName):
        # TODO : implement later. Should return True or False whether download successfully completed or not

        return True

    def get_dir(self, remoteDir, recurse=False):
         # TODO : implement later. Same as get_file but for all files in specified directory

        return True

    def is_file_downloaded(self, remoteDir, fileName):
        # TODO : implement later. Should return True or False whether the file is present locally, and with the same size as the remote version.

        return True

    def is_dir_downloaded(self, remoteDir, recurse=False):
        # TODO : implement later. Same as is_file_downloaded but for all files in specified directory

        return True

    def get_file_progress(self, remoteDir, fileName):
        # TODO : implement later. Should return, for a file currently being downloaded, the % of completion. Not sure if possible though ?

        return 0

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

