# Author: orion1024 <orion1024@gmail.com>
# URL: https://github.com/orion1024/Sick-Beard
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

class SeedboxDownloader():
    
    def __init__(self, ftpHost=None, ftpUser=None, ftpKey=None, ftpPassword=None, remoteDir=None, localDir=None):
        self.ftpHost = ftpHost
        self.ftpUser = ftpUser
        self.ftpKey = ftpKey
        self.ftpPassword = ftpPassword
        self.remoteDir = remoteDir
        self.localDir = localDir


    def run(self):

        logger.log(u"Checking seedbox for files...", logger.MESSAGE)
        logger.log(u"Not really doing anything yet", logger.MESSAGE)

