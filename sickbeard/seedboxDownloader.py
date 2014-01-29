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

from sickbeard import logger

# This class will populate the download queue, primarily by using the protocol wrapper to list remote files to be downloaded.
class SeedboxDownloader():
    
    def __init__(self, *args):
        # TODO : implement later

        self.wrapper = SeedboxDownloaderProtocolWrapper(*args)


    def run(self):
        # TODO : implement later
        logger.log(u"Checking seedbox for files...", logger.MESSAGE)
        logger.log(u"Not really doing anything yet", logger.MESSAGE)

# This class is meant to hold necessary information to properly call the wrapper methods.
# The downloader will build these objects and supply them to the queue items so that the files get downloaded.
class SeedboxDownload():
    
    def __init__(self, remoteDir, fileName):
        # TODO : implement later
        self.remoteDir = remoteDir
        self.fileName = fileName
        



# This class is meant to present common methods to use to download files, whatever transfer protocol is used.
# It is used by the seedbox downloader (to list the remote files to download and populate the queue with them) and the queue itself (to actually download said files)
# At first only SFTP will be supported, but it will make adding other protocols easier
class SeedboxDownloaderProtocolWrapper():
    
    def __init__(self, protocol, remoteHost, remoteRootDir, landingDir, remoteUser=None, remoteAuthKey=None, remotePassword=None):
        # TODO : implement later. There should a logic to check the consistency of parameters.
        self.protocol = protocol
        self.remoteHost = remoteHost
        self.remoteUser = remoteUser
        self.remoteAuthKey = remoteAuthKey
        self.remotePassword = remotePassword
        self.remoteRootDir = remoteRootDir
        self.landingDir = landingDir

        self.validConfiguration = True

    def list_dir(self, remoteDir, recursive=False)
        # TODO : implement later
        results = []

        return results

    def get_file(self, remoteDir, fileName)
        # TODO : implement later. Should return True or False whether download successfully completed or not

        return True

    def get_dir(self, remoteDir, recurse=False)
         # TODO : implement later. Same as get_file but for all files in specified directory

        return True

    def is_file_downloaded(self, remoteDir, fileName)
        # TODO : implement later. Should return True or False whether the file is present locally, and with the same size as the remote version.

        return True

    def is_dir_downloaded(self, remoteDir, recurse=False)
        # TODO : implement later. Same as is_file_downloaded but for all files in specified directory

        return True

    def get_file_progress(self, remoteDir, fileName)
        # TODO : implement later. Should return, for a file currently being downloaded, the % of completion. Not sure if possible though ?

        return 0

    def is_dir_downloaded(self, remoteDir, recurse=False)
        # TODO : implement later. Same as is_file_downloaded but for all files in specified directory

        return True


    def delete_file(self, remoteDir, fileName)
        # TODO : implement later. Should return True or False whether the file deletion successfully completed or not

        return True

    def delete_dir(self, remoteDir, recurse=False)
         # TODO : implement later. Same as delete_file but for all files in specified directory


