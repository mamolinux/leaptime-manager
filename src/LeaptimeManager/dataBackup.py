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
import gi
import locale
import logging
import os

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
module_logger = logging.getLogger('LeaptimeManager.dataBackup')

class UserData_backend():
	
	def __init__(self) -> None:
		module_logger.info("Init UserData_backend class...")

class UserData():
	"""
	GUI class for backing up and restoring user data
	using rsync
	"""
	def __init__(self) -> None:
		module_logger.info("Init UserData class...")
	
	def choose_dirs(self, title, widget):
		# Choose source/destination directory for data backup
		selected_dir = ""
		dialog = Gtk.FileChooserDialog(
			title=title,
			action=Gtk.FileChooserAction.SELECT_FOLDER,
		)
		dialog.set_transient_for(widget)
		dialog.add_buttons(
			Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, "Select", Gtk.ResponseType.OK
		)
		dialog.set_default_size(800, 400)
		
		response = dialog.run()
		if response == Gtk.ResponseType.OK:
			module_logger.debug("Folder selected: %s", dialog.get_filename())
			selected_dir = dialog.get_filename()
		else:
			selected_dir = ""
		
		dialog.destroy()
		return selected_dir
	
	def on_select_src(self, widget):
		title = "Please choose source folder"
		self.source_dir = self.choose_dirs(title, widget)
	
	def on_select_dest(self, widget):
		title = "Please choose destination folder"
		self.backup_dir = self.choose_dirs(title, widget)
	
	def on_backup_data(self):
		module_logger.info("Starting backup using Rsync...")
		if self.source_dir and self.backup_dir:
			cmd = "rsync -aAXUH --checksum --compress --partial %s %s" % (self.source_dir, self.backup_dir)
			module_logger.debug("Running command: %s" % cmd)
			os.system(cmd)
			module_logger.info("%s is backed up into %s" % (self.source_dir, self.backup_dir))
		else:
			if not self.source_dir:
				module_logger.error("No source directory selected.")
			if not self.backup_dir:
				module_logger.error("No destination directory selected.")
	
	def userData(self, widget):
		module_logger.info("Starting Data backup...")
		self.on_select_src(widget)
		self.on_select_dest(widget)
		self.on_backup_data()
