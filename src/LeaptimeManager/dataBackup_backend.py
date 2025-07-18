# Copyright (C) 2021-2024 Himadri Sekhar Basu <hsb10@iitbbs.ac.in>
# 
# This file is part of LeapTime Manager.
# 
# LeapTime Manager is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# LeapTime Manager is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with LeapTime Manager. If not, see <http://www.gnu.org/licenses/>
# or write to the Free Software Foundation, Inc., 51 Franklin Street,
# Fifth Floor, Boston, MA 02110-1301, USA..
# 
# Author: Himadri Sekhar Basu <hsb10@iitbbs.ac.in>
#

# import the necessary modules!
import gettext
import locale
import logging
import os
import random
import stat
import string

# imports from current package
from LeaptimeManager.cli_args import  APP, LOCALE_DIR
from LeaptimeManager.database_rw import databackup_db
from LeaptimeManager.dialogs import show_message

# i18n
locale.bindtextdomain(APP, LOCALE_DIR)
gettext.bindtextdomain(APP, LOCALE_DIR)
gettext.textdomain(APP)
_ = gettext.gettext

# logger
module_logger = logging.getLogger('LeaptimeManager.dataBackup_backend')


class UserData_backend():
	def __init__(self, errors) -> None:
		module_logger.info(_("Initializing User Data backend class..."))
		
		# inidicates whether an operation is taking place.
		self.operating = False
		
		# backup default settings
		self.follow_links = True
		
		self.errors = errors
		self.db_manager = databackup_db()
	
	def back_compat(self, window):
		# Do a backward compatibility check
		module_logger.debug(_("Checking backward compatibility of data backups."))
		self.temp_data_db_list = []
		self.data_db_list = self.db_manager.read_db()
		for backup in self.data_db_list:
			if (not "uuid" in backup) or (len(backup["uuid"]) != 8) :
				show_message(window, _("Selected data backup was created using an older version. This backup will now be updated to work with the current version. But, there is a possibility that it might not work. Check the logs and report any issue."))
				backup["uuid"] = ''.join(random.choice(string.digits+string.ascii_letters) for _ in range(8))
			
			if not "method" in backup:
				if "filename" in backup:
					backup["method"] = "tarball"
				else:
					backup["method"] = "rsync"
			
			if not "exclude" in backup:
				backup["exclude"] = ""
			if not "include" in backup:
				backup["include"] = ""
			
			if not "count" in backup:
				backup["count"] = ""
			if not "size" in backup:
				backup["size"] = ""
			
			data_backup_dict = {
				"uuid" : backup["uuid"],
				"name" : backup["name"],
				"method" : backup["method"],
				"source" : backup["source"],
				"destination" : backup["destination"],
				"filename": backup["filename"],
				"created" : backup["created"],
				"repeat" : backup["repeat"],
				"comment" : backup["comment"],
				"exclude" : backup["exclude"],
				"include" : backup["include"],
				"count" : backup["count"],
				"size" : backup["size"],
			}
			
			self.temp_data_db_list.append(data_backup_dict)
			self.db_manager.write_db(self.temp_data_db_list)
	
	def scan_dirs(self, operating, source_dir, excluded_files, excluded_dirs, included_files, included_dirs, callback):
		self.operating = operating
		self.source_dir = source_dir
		self.excluded_files = excluded_files
		self.excluded_dirs = excluded_dirs
		self.included_files = included_files
		self.included_dirs = included_dirs
		self.num_files = 0
		self.total_size = 0
		copy_files = []
		for top, dirs, files in os.walk(top=self.source_dir, onerror=None, followlinks=self.follow_links):
			if not self.operating:
				break
			if top == self.source_dir:
				# Remove hidden dirs in the root of the source directory
				dirs[:] = [d for d in dirs if (not d.startswith(".") or os.path.join(top, d) in self.included_dirs)]
			# Remove excluded dirs in the source directory
			dirs[:] = [d for d in dirs if (not os.path.join(top, d) in self.excluded_dirs)]
			
			for f in files:
				if not self.operating:
					break
				if top == self.source_dir:
					# Skip hidden files in the root of the source directory, unless included
					if f.startswith(".") and os.path.join(top, f) not in self.included_files:
						continue
				path = os.path.join(top, f)
				if os.path.exists(path):
					if os.path.islink(path) and not self.follow_links:
						# Skip links if appropriate
						continue
					if stat.S_ISFIFO(os.stat(path).st_mode):  # If file is a named pipe
						# Skip named pipes, they can cause program to hang.
						self.errors.append([_("Skipping %s because named pipes are not supported.") % path, None])
						continue
					if path not in self.excluded_files:
						callback(path)
						copy_files.append(path)
		
		copy_files.sort()
		
		return (copy_files, self.num_files, self.total_size)
	
	def callback_count_total(self, path):
		file_size = os.path.getsize(path)
		self.total_size += file_size
		self.num_files += 1
	
	def write_log(self, backup_logfile, backuplog):
		with open(backup_logfile, "a") as logfile:
			logfile.write(backuplog)
