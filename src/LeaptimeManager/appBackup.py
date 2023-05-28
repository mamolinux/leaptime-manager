# Copyright (C) 2021-2023 Himadri Sekhar Basu <hsb10@iitbbs.ac.in>
# 
# This file is part of leaptime-manager.
# 
# leaptime-manager is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# leaptime-manager is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with leaptime-manager.  If not, see <http://www.gnu.org/licenses/>
# or write to the Free Software Foundation, Inc., 51 Franklin Street,
# Fifth Floor, Boston, MA 02110-1301, USA..
# 
# Author: Himadri Sekhar Basu <hsb10@iitbbs.ac.in>
#
# A shameless partial rip-off from MintBackup tool

# import the necessary modules!
import apt
# from apt import package
import apt_pkg
import gettext
import gi
import locale
import logging
import os
import time

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

# imports from current package
from LeaptimeManager.common import APP, LOCALE_DIR

# i18n
locale.bindtextdomain(APP, LOCALE_DIR)
gettext.bindtextdomain(APP, LOCALE_DIR)
gettext.textdomain(APP)
_ = gettext.gettext

# logger
module_logger = logging.getLogger('LeaptimeManager.appBackup')

class AppBackup():
	
	def __init__(self) -> None:
		module_logger.info("Work in progress...")
	
	def choose_dirs(self, widget):
		# Choose directory to save app backup files
		dialog = Gtk.FileChooserDialog(
			title="Please choose a folder",
			action=Gtk.FileChooserAction.SELECT_FOLDER,
		)
		dialog.set_transient_for(widget)
		dialog.add_buttons(
			Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, "Select", Gtk.ResponseType.OK
		)
		dialog.set_default_size(800, 400)

		response = dialog.run()
		if response == Gtk.ResponseType.OK:
			print("Select clicked")
			print("Folder selected: " + dialog.get_filename())
			module_logger.debug("Folder selected: %s", dialog.get_filename())
			self.backup_dir = dialog.get_filename()
		
		dialog.destroy()
	
	def backup_pkg(self):
		apt_pkg.init()
		
		cache = apt_pkg.Cache()					# all cache packages
		# package object list of all available packages in all repo
		allpacks_list = [pack for pack in cache.packages]
		
		installer_log = "/var/log/installer/initial-status.gz"
		if not os.path.isfile(installer_log):
			return None
		import gzip
		try:
			installer_log = gzip.open(installer_log, "r").read().decode('utf-8').splitlines()
		except Exception as e:
			# There are a number of different exceptions here, but there's only one response
			print("Could not get initial installed packages list (check /var/log/installer/initial-status.gz): %s" % str(e))
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
				# print(pack.name, "is installed.")
			else:
				pass
			# list all auto-installed packages
			if apt_pkg.DepCache(cache).is_auto_installed(pack):
				auto_installed_pkgs.append(pack.name)
				# print(pack.name, "is auto installed.")
			else:
				pass
		
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
	
	def backup_pkg_save_to_file(self):
		
		installed_packages=self.backup_pkg()
		# Save the package selection
		filename = time.strftime("%Y-%m-%d-%H%M-packages.list", time.localtime())
		file_path = os.path.join(self.backup_dir, filename)
		with open(file_path, "w") as f:
			for pack in installed_packages:
				f.write("%s\t%s\n" % (pack, "install"))
	
	def restore_pkg_validate_file(self, filechooser):
		# Check the file validity
		self.package_source = filechooser.get_filename()
		try:
			with open(self.package_source, "r") as source:
				error = False
				for line in source:
					line = line.rstrip("\r\n")
					if line != "":
						if not line.endswith("\tinstall") and not line.endswith(" install"):
							self.show_message(_("The selected file is not a valid software selection."))
							self.builder.get_object("button_forward").set_sensitive(False)
							return
			self.builder.get_object("button_forward").set_sensitive(True)
		except Exception as detail:
			self.show_message(_("An error occurred while reading the file."))
			print (detail)

if __name__ == "__main__":
	AppBackup()
