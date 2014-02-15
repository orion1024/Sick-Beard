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
import shutil

import sickbeard
from sickbeard import logger

from lib.pysftp import pysftp

import seedboxDownload_queue
import seedboxDownloadHelpers
from seedboxDownloadHelpers import print_bytes

# This class will populate the download queue, primarily by using the protocol wrapper to list remote files to be downloaded.
class SeedboxDownloader():
    
    def __init__(self):
        
        
        self.downloads = []
        self.download_queue = seedboxDownload_queue.SeedboxDownloadQueue()
        
        # Initializing stats variables
        self.total_files = 0
        self.total_downloaded_files = 0
        self.total_already_present_files = 0
        self.total_files_to_download = 0
        self.total_downloaded_bytes = 0
        self.total_bytes_to_download = 0
        
        # Getting the settings from sickbeard
        self.settings = seedboxDownloadHelpers.SeedboxDownloaderSettings()
        self.reload_settings()
        
        #self.discover_protocol_wrapper = SeedboxDownloaderProtocolWrapper(*args)
        self.discover_protocol_wrapper = seedboxDownloadHelpers.SeedboxDownloaderProtocolWrapper(self.settings.protocol_settings)
        # TODO : for the moment we use a wrapper for the queue. It isn't ideal if this one hangs. Should I just create a new wrapper when each file is downloading ?
        # maybe pass on a wrapper setting object that allows the download object to rebuild a wrapper when its current one fails. Food for thought !
        self.queue_protocol_wrapper = seedboxDownloadHelpers.SeedboxDownloaderProtocolWrapper(self.settings.protocol_settings)            

    
    # Reload settings from sickbeard configuration
    def reload_settings(self):
        
        logger.log(u"Reloading Seedbox Download settings from sickbeard configuration.", logger.DEBUG)
        
        # General settings
        self.settings.enabled=sickbeard.SEEDBOX_DOWNLOAD_ENABLED
        
        # Update queue items with the new setting for deletion if modified
        if not self.settings.delete_remote_files == sickbeard.SEEDBOX_DOWNLOAD_DELETE_REMOTE_FILES:
            for queue_item in self.download_queue.queue:
                queue_item.remove_remote_on_success = sickbeard.SEEDBOX_DOWNLOAD_DELETE_REMOTE_FILES
                
        self.settings.delete_remote_files=sickbeard.SEEDBOX_DOWNLOAD_DELETE_REMOTE_FILES
        self.settings.automove_in_postprocess_dir=sickbeard.SEEDBOX_DOWNLOAD_AUTOMOVE_IN_POSTPROCESS_DIR
        self.settings.check_frequency=sickbeard.SEEDBOX_DOWNLOAD_CHECK_FREQUENCY
        self.settings.landing_dir=sickbeard.SEEDBOX_DOWNLOAD_LANDING_DIR
        self.settings.download_episodes_only=sickbeard.SEEDBOX_DOWNLOAD_DOWNLOAD_EPISODE_ONLY
        
        # SFTP Settings
        self.settings.protocol_settings.protocol=sickbeard.SEEDBOX_DOWNLOAD_PROTOCOL
        self.settings.protocol_settings.sftp_remote_host=sickbeard.SEEDBOX_DOWNLOAD_SFTP_HOST
        self.settings.protocol_settings.sftp_remote_port=sickbeard.SEEDBOX_DOWNLOAD_SFTP_PORT
        self.settings.protocol_settings.sftp_remote_root_dir=sickbeard.SEEDBOX_DOWNLOAD_SFTP_REMOTE_ROOT_DIR
        self.settings.protocol_settings.sftp_remote_user=sickbeard.SEEDBOX_DOWNLOAD_SFTP_USERNAME
        self.settings.protocol_settings.sftp_remote_auth_key=sickbeard.SEEDBOX_DOWNLOAD_SFTP_CERT_FILE
        self.settings.protocol_settings.sftp_remote_password=sickbeard.SEEDBOX_DOWNLOAD_SFTP_PASSWORD
        self.settings.protocol_settings.sftp_landing_dir=sickbeard.SEEDBOX_DOWNLOAD_LANDING_DIR
        self.settings.protocol_settings.sftp_use_cert=sickbeard.SEEDBOX_DOWNLOAD_SFTP_USE_CERT
       
        # TEMP
        #self.settings.protocol_settings.protocol="SFTP"
        #self.settings.protocol_settings.sftp_remote_host="localhost"
        #self.settings.protocol_settings.sftp_landing_dir=sickbeard.SEEDBOX_DOWNLOAD_LANDING_DIR
        #self.settings.protocol_settings.sftp_remote_port=""
        #self.settings.protocol_settings.sftp_remote_root_dir="myremotedir"
        #self.settings.protocol_settings.sftp_remote_user="sftp"
        #self.settings.protocol_settings.sftp_remote_auth_key=sickbeard.SEEDBOX_DOWNLOAD_SFTP_CERT_FILE
        #self.settings.protocol_settings.sftp_remote_password="p59kN85vTaqnkGoEJsgt"
        #self.settings.protocol_settings.sftp_use_cert=False
         
        if self.settings.enabled:
            if self.download_queue.is_download_paused():
                logger.log(u"Seedbox download has been enabled, unpausing the download queue.", logger.MESSAGE)
                self.download_queue.unpause_download()
        elif not self.download_queue.is_download_paused():
                logger.log(u"Seedbox download has been disabled, pausing the download queue.", logger.MESSAGE)
                self.download_queue.pause_download()
        
        
        return

    # This method is called at the SEEDBOX_DOWNLOAD_CHECK_FREQUENCY by the scheduler defined in sickbeard namespace.
    def run(self):
        
        # If feature is disabled, don't do anything
        if self.settings.enabled:


            logger.log(u"Checking seedbox for files...", logger.MESSAGE)
               
            new_downloads = self.discover_protocol_wrapper.list_dir(recursive=True)   
            
            logger.log(u"Got %d results. Computing stats..." % len(new_downloads), logger.MESSAGE)
                        
            self.discover_protocol_wrapper.check_already_present_downloads(new_downloads)      
           
            # TODO : remove this line later when testing is over.
            for download in self.downloads:
                if download.file_download_failed:
                    logger.log(u"Failed download : %s (%s)" % (download.Name, download.file_download_error), logger.MESSAGE)
            
            self.add_new_downloads(new_downloads)
            
            if self.settings.automove_in_postprocess_dir:
                self.move_downloads_to_postprocess_dir()

            
            self.update_download_stats()
            self.log_download_stats()
            
        return          

    # Iterates against all known downloads and move them to the post-process directory.
    def move_downloads_to_postprocess_dir(self):
        
        move_count = 0
        if os.path.exists(sickbeard.TV_DOWNLOAD_DIR):
            
            for download in self.downloads:
                                
                if (download.file_downloaded or download.file_already_present) and not download.file_moved:
                    
                    # we move the file in a post process subdirectory relative to the landing directory
                    post_process_subdir = os.path.normpath(os.path.join(sickbeard.TV_DOWNLOAD_DIR, os.path.relpath(os.path.dirname(download.local_file_path), self.settings.landing_dir)))
                    
                    # First we create the necessary directories then we move the file in it.
                    if not os.path.exists(post_process_subdir):
                        try:
                            os.makedirs(post_process_subdir)
                        except IOError as IOException:
                            logger.log(u"Error when trying to create post process subdir %s : %s" % (post_process_subdir, str(IOException)), logger.DEBUG)
                    else:
                        try:
                            shutil.move(download.local_file_path, post_process_subdir)
                        except shutil.Error as errorException :
                            logger.log(u"Error when trying to move file %s to post process dir : %s" % (download.Name, str(errorException)), logger.DEBUG)
                        except IOError as IOException :
                            logger.log(u"Error when trying to move file %s to post process dir : %s" % (download.Name, str(IOException)), logger.DEBUG)
                        
                        else:
                            download.file_moved = True
                            move_count = move_count + 1
                            logger.log(u"File %s successfully moved to post-process dir." % (download.Name), logger.DEBUG)
                # TODO : remove empty dir
        else:
            logger.log(u"Post-process directory not found, not moving downloaded files into it. Directory is %s" % sickbeard.TV_DOWNLOAD_DIR, logger.ERROR)
        
        logger.log(u"%d file(s) moved to post-process directory." % move_count, logger.MESSAGE)    
        
        return
    
    # Add new downloads if it isn't already in the list, to the internal list AND to the queue.
    def add_new_downloads(self, new_downloads):
        
        new_download_count = 0
        for new_download in new_downloads:
            if not self.is_download_known(new_download):
                self.downloads.append(new_download)
                if not new_download.file_already_present:
                    self.download_queue.add_item(seedboxDownload_queue.DownloadQueueItem(new_download, self.queue_protocol_wrapper, self.settings.delete_remote_files))
                    new_download_count += 1
                    
        logger.log(u"%d new files to download." % new_download_count, logger.MESSAGE)
        return

    # Returns True if the download object given already exists in the list of downloads.
    def is_download_known(self, new_download):
    
        for download in self.downloads:
            if download.remote_file_path == new_download.remote_file_path:
                return True
        
        return False

        
    # Computes stats about all downloads : total size, number of downloaded files, downloaded bytes until now...
    def update_download_stats(self):
        
        self.total_files = 0
        self.totalBytes = 0
        self.total_downloaded_files = 0
        self.total_downloaded_bytes = 0
        self.total_already_present_files = 0
        self.totalAlreadyPresentBytes = 0
        self.total_files_to_download = 0
        self.total_bytes_to_download = 0

        
        for download in self.downloads:
            self.total_files += 1
            self.totalBytes += download.file_size
 
            # A file is either downloaded (implicitely in this session), already present (previously downloaded), or in the queue          
            if download.file_downloaded:
                self.total_downloaded_files += 1
                self.total_downloaded_bytes += download.file_size
            elif download.file_already_present:
                self.total_already_present_files += 1
                self.totalAlreadyPresentBytes += download.file_size  
            else:
                self.total_files_to_download += 1
                # If file is currently downloading, we take the transferred_bytes into account
                if download.file_downloading:
                    self.total_bytes_to_download += download.file_size - download.transferred_bytes
                    self.total_downloaded_bytes += download.transferred_bytes
                else:
                    self.total_bytes_to_download += download.file_size
                
        return

    # Logs stats to Sickbeard log file : total size, number of downloaded files, downloaded bytes until now...
    def log_download_stats(self):
        # TODO : complete later
        logger.log(u"Total files : %d (%s)" % (self.total_files,print_bytes(self.totalBytes)), logger.MESSAGE)
        logger.log(u"Total downloaded files : %d (%s)" % (self.total_downloaded_files,print_bytes(self.total_downloaded_bytes)), logger.MESSAGE)
        logger.log(u"Total files already present : %d (%s)" % (self.total_already_present_files,print_bytes(self.totalAlreadyPresentBytes)), logger.MESSAGE)
        logger.log(u"Total files to download : %d (%s)" % (self.total_files_to_download,print_bytes(self.total_bytes_to_download)), logger.MESSAGE)
        logger.log(u"Total files in download queue : %d" % (len(self.download_queue.queue)), logger.MESSAGE)

        
        return
    
    # Called when Sickbeard is stopping itself.
    def cleanup(self):
        
        try:
            # We want to move all downloaded files to post-process dir before going down.
            if self.settings.automove_in_postprocess_dir:
                self.move_downloads_to_postprocess_dir()
        except:
            # as we are ending processes, we catch any exception and simply display it in the log.
            logger.log(u"Error while cleanup, when trying to move files to post-process directory : %s" % (sys.exc_info()[0]), logger.DEBUG)
        
        
        # TODO : close cleanly wrappers. Halt transfer ?
        
        return

