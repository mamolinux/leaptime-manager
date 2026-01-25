# Copyright (C) 2021-2023 Himadri Sekhar Basu <hsb10@iitbbs.ac.in>
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
import string
import sys
import tarfile
import time

from pathlib import Path

# imports from current package
from LeaptimeManager.cli_args import  APP, LOCALE_DIR
from LeaptimeManager.common import DATA_LOG_DIR
from LeaptimeManager.database_rw import databackup_db
from LeaptimeManager.dataBackup_backend import UserData_backend

# i18n
locale.bindtextdomain(APP, LOCALE_DIR)
gettext.bindtextdomain(APP, LOCALE_DIR)
gettext.textdomain(APP)
_ = gettext.gettext

# logger
module_logger = logging.getLogger('LeaptimeManager.tarball_backend')

# Constants
META_FILE = ".meta"

class tar_backend():
	def __init__(self, errors) -> None:
		module_logger.info(_("Initializing tarball manager backend class..."))
		self.errors = errors
		self.db_manager = databackup_db()
		self.manager = UserData_backend(self.errors)
		self.operating = self.manager.operating
		self.data_db_list = self.db_manager.read_db()
	
	def prep_tar_backup(self, backup_name, source_dir, dest_dir, excluded_files, excluded_dirs, included_files, included_dirs, tar_backup_format, repeat=False):
		self.repeat = repeat
		self.uuid = ''.join(random.choice(string.digits+string.ascii_letters) for _ in range(8))
		self.backup_name = backup_name
		self.source_dir = source_dir
		self.dest_dir = dest_dir
		self.excluded_files = excluded_files
		self.excluded_dirs = excluded_dirs
		self.included_files = included_files
		self.included_dirs = included_dirs
		self.tar_backup_format = tar_backup_format
		time_now = time.localtime()
		self.timestamp = time.strftime("%Y-%m-%d %H:%M", time_now)
		self.temp_filename = os.path.join(self.dest_dir, "%s-%s.%s.part" % (self.backup_name, time.strftime("%Y-%m-%d_%H-%M", time_now), self.tar_backup_format))
		self.tarfilename = os.path.join(self.dest_dir, "%s-%s.%s" % (self.backup_name, time.strftime("%Y-%m-%d_%H-%M", time_now), self.tar_backup_format))
		backuplogdir = os.path.join(DATA_LOG_DIR, backup_name)
		Path(backuplogdir).mkdir(parents=True, exist_ok=True)
		self.backup_logfile = os.path.join(backuplogdir, backup_name + "_" + self.timestamp + '.log')
		
		self.operating = True
		self.num_files = 0
		self.total_size = 0
		os.chdir(self.source_dir)
		
		try:
			if self.tar_backup_format == "tar":
				self.backup_mode = "w"
			elif self.tar_backup_format == "tar.gz":
				self.backup_mode = "w:gz"
			elif self.tar_backup_format == "tar.bz2":
				self.backup_mode = "w:bz2"
			elif self.tar_backup_format == "tar.xz":
				self.backup_mode = "w:xz"
			else:
				module_logger.error("Invalid format %s. Please choose between tar, tar.gz, tar.bz2 or tar.xz." % self.tar_backup_format)
				self.operating = False
				sys.exit(1)
			
			# get a count of all the files
			module_logger.debug(_(f"Number of files: {self.num_files}, Total size in byte: {self.total_size}"))
			module_logger.debug(_(f"List of files to copy: {"\n".join(self.copy_files)}"))
			
			# Create META file
			try:
				of = os.path.join(self.dest_dir, META_FILE)
				lines = ["num_files: %s\ntotal_size: %s\n" % (self.num_files, self.total_size)]
				with open(of, "w") as out:
					out.writelines(lines)
			except Exception as detail:
				print(detail)
				self.errors.append([_("Warning: The meta file could not be saved. This backup will not be accepted for restoration."), None])
			
			return (self.timestamp, self.tarfilename, self.num_files, self.total_size, self.copy_files)
		except Exception as e:
			print(e)
	
	def add_meta_tar_backup(self):
		try:
			self.tar_archive = None
			
			try:
				self.tar_archive = tarfile.open(name=self.temp_filename, dereference=self.manager.follow_links, mode=self.backup_mode, bufsize=1024)
				metafile = os.path.join(self.dest_dir, META_FILE)
				self.tar_archive.add(metafile, arcname=META_FILE, recursive=False)
				os.remove(metafile)
			except Exception as detail:
				print(detail)
				self.errors.append([str(detail), None])
		except Exception as e:
			print(e)
	
	def finish_tar_backup(self, backuplog, desc="", backup_method="tarball"):
		self.backup_method = backup_method
		self.backup_desc = desc
		try:
			try:
				self.tar_archive.close()
				os.rename(self.temp_filename, self.tarfilename)
				self.manager.write_log(self.backup_logfile, backuplog)
				data_backup_dict = {
					"uuid" : self.uuid,
					"name" : self.backup_name,
					"method" : self.backup_method,
					"source" : self.source_dir,
					"destination" : self.dest_dir,
					"filename": os.path.basename(self.tarfilename),
					"created" : self.timestamp,
					"repeat" : self.repeat,
					"comment" : self.backup_desc,
					"exclude" : (self.excluded_dirs, self.excluded_files),
					"include" : (self.included_dirs, self.included_files),
					"logfile" : self.backup_logfile,
					"count" : self.num_files,
					"size" : self.total_size,
					}
				self.data_db_list.append(data_backup_dict)
				self.db_manager.write_db(self.data_db_list)
			except Exception as detail:
				print(detail)
				self.errors.append([str(detail), None])
			
			if self.archived_files < self.num_files:
				self.errors.append([_("Warning: Some files were not saved. Only %(archived)d files were backed up out of %(total)d.") % {'archived': self.archived_files, 'total': self.num_files}, None])
		
		except Exception as e:
			print(e)
	
	def callback_add_to_tar(self, path, archived_files, archived_file_size):
		try:
			self.archived_files = archived_files
			self.archived_file_size = archived_file_size
			rel_path = os.path.relpath(path)
			self.tar_archive.add(path, arcname=rel_path, recursive=False)
			self.archived_files += 1
			archived_file_size = os.path.getsize(path)
			self.archived_file_size += archived_file_size
			backuplog = "[%s]: %s    -->    %s\n" % (str(self.archived_files), path, self.tarfilename)
			module_logger.info(backuplog)
			return (self.archived_files, self.archived_file_size, backuplog)
		except Exception as detail:
			print(detail)
			self.errors.append([path, str(detail)])
			return
	