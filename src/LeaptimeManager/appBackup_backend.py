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
# A shameless partial rip-off from MintBackup tool

# import the necessary modules!
import os
import random
import string
import time
import gzip
import gettext
import apt
import apt_pkg
import logging
import locale

from gi.repository import GLib
# from aptdaemon.enums import *

# imports from current package
from LeaptimeManager.cli_args import APP, LOCALE_DIR
from LeaptimeManager.database_rw import appbackup_db

# i18n
locale.bindtextdomain(APP, LOCALE_DIR)
gettext.bindtextdomain(APP, LOCALE_DIR)
gettext.textdomain(APP)
_ = gettext.gettext

# logger
module_logger = logging.getLogger('LeaptimeManager.appBackup_backend')

class AppBackup_backend():
	def __init__(self) -> None:
		self.db_manager = appbackup_db()
	
	def backup_pkg_list(self, cache):
		self.cache = cache
		# package object list of all available packages in all repo
		allpacks_list = [pack for pack in self.cache.packages]
		
		installer_log = "/var/log/installer/initial-status.gz"
		if not os.path.isfile(installer_log):
			module_logger.error("%s does not exist." % installer_log)
			return None
		try:
			installer_log = gzip.open(installer_log, "r").read().decode('utf-8').splitlines()
		except Exception as e:
			# There are a number of different exceptions here, but there's only one response
			module_logger.error("Could not get initial installed packages list (check /var/log/installer/initial-status.gz): %s" % str(e))
			return None
		initial_status = [x[9:] for x in installer_log if x.startswith("Package: ")]
		if not initial_status:
			return None
		
		installed_pkgs = []
		auto_installed_pkgs = []
		for pack in allpacks_list:
			# list all installed packages
			if apt.Package(any, pack).is_installed:
				installed_pkgs.append(pack.name)
				# module_logger.debug(pack.name, " is installed.")
			# list all auto-installed packages
			if apt_pkg.DepCache(self.cache).is_auto_installed(pack):
				auto_installed_pkgs.append(pack.name)
				# module_logger.debug(pack.name, " is auto installed.")
		
		# sort installed packages and auto-installed packages
		installed_pkgs.sort()
		auto_installed_pkgs.sort()
		# find packages marked as manual
		marked_manual_pakgs = []
		for pack in installed_pkgs:
			if pack not in auto_installed_pkgs:
				marked_manual_pakgs.append(pack)
		
		# Manually installed packages
		installed_packages = []
		for pack in installed_pkgs:
			if pack not in initial_status:
				if pack in marked_manual_pakgs:
					installed_packages += [pack]
		
		return installed_packages
	
	def create_installed_pkg_list(self, cache):
		self.cache = cache
		self.installed_packages = self.backup_pkg_list(self.cache)
		package_records = apt_pkg.PackageRecords(self.cache)
		installed_pkg_list = []
		try:
			for name in self.installed_packages:
				if name in self.cache:
						pkg = self.cache[name]
						if pkg.current_ver:
							package_records.lookup(pkg.version_list[0].translated_description.file_list[0])
							desc = "%s\n<small>%s</small>" % (pkg.name, GLib.markup_escape_text(package_records.short_desc))
							installed_pkg_list.append([True, pkg.name, desc])
		except Exception as e:
			print(e)
		
		module_logger.debug("Found manually installed Packages: %s" % installed_pkg_list)
		return installed_pkg_list
	
	def pkg_backup_save_to_file(self, backup_name, backup_dest, cache, repeat=""):
		# Save the package selection
		uuid = ''.join(random.choice(string.digits+string.ascii_letters) for _ in range(8))
		time_now = time.localtime()
		self.timestamp = time.strftime("%Y-%m-%d %H:%M", time_now)
		self.filename = backup_name+"_"+time.strftime("%Y-%m-%d-%H%M", time_now)+"-packages.list"
		file_path = os.path.join(backup_dest, self.filename)
		installed_pkg_list = self.create_installed_pkg_list(cache)
		with open(file_path, "w") as f:
			for row in installed_pkg_list:
				if row[0]:
					f.write("%s\t%s\n" % (row[1], "install"))
		self.repeat = repeat
		app_backup_dict = {
			"uuid" : uuid,
			"name" : backup_name,
			"filename" : self.filename,
			"created" : self.timestamp,
			"repeat" : self.repeat,
			"location" : backup_dest,
			"last_run" : self.timestamp
		}

		self.app_db_list.append(app_backup_dict)
		self.db_manager.write_db(self.app_db_list)

	def execute_scheduled_backup(self, backup_name, backup_dest, cache):
		"""Execute a scheduled backup and update the last_run timestamp."""
		uuid = ''.join(random.choice(string.digits+string.ascii_letters) for _ in range(8))
		time_now = time.localtime()
		timestamp = time.strftime("%Y-%m-%d %H:%M", time_now)
		filename = backup_name+"_"+time.strftime("%Y-%m-%d-%H%M", time_now)+"-packages.list"
		file_path = os.path.join(backup_dest, filename)
		installed_pkg_list = self.create_installed_pkg_list(cache)

		try:
			with open(file_path, "w") as f:
				for row in installed_pkg_list:
					if row[0]:
						f.write("%s\t%s\n" % (row[1], "install"))

			module_logger.info(_("Scheduled backup executed: %s") % backup_name)
			return True
		except Exception as e:
			module_logger.error(_("Failed to execute scheduled backup %s: %s") % (backup_name, str(e)))
			return False
	
	def back_compat(self):
		# Do a backward compatibility check
		module_logger.debug(_("Checking backward compatibility of app backups."))
		self.app_db_list = self.db_manager.read_db()
		self.temp_app_db_list = []
		for backup in self.app_db_list:
			if (not "uuid" in backup) or (len(backup["uuid"]) != 8) :
				module_logger.warning(_("Selected app backup was created using an older version. This backup will now be updated to work with the current version. But, there is a possibility that it might not work. Check the logs and report any issue."))
				backup["uuid"] = ''.join(random.choice(string.digits+string.ascii_letters) for _ in range(8))

			# Add last_run field if missing for backward compatibility
			if "last_run" not in backup:
				backup["last_run"] = backup.get("created", "")

			app_backup_dict = {
				"uuid" : backup["uuid"],
				"name" : backup["name"],
				"filename" : backup["filename"],
				"created" : backup["created"],
				"repeat" : backup["repeat"],
				"location" : backup["location"],
				"last_run" : backup["last_run"]
			}

			self.temp_app_db_list.append(app_backup_dict)
			self.db_manager.write_db(self.temp_app_db_list)
