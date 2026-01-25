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
import apt_pkg
import gettext
import gi
import locale
import logging
import os
import subprocess
import aptdaemon.client
import aptdaemon.errors

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib
from aptdaemon.enums import *
from aptdaemon.gtk3widgets import (AptConfirmDialog, AptErrorDialog,
								   AptProgressDialog, AptStatusIcon)

# imports from current package
from LeaptimeManager.cli_args import APP, LOCALE_DIR
from LeaptimeManager.database_rw import appbackup_db
from LeaptimeManager.appBackup_backend import AppBackup_backend
from LeaptimeManager.dialogs import show_message, delete_confirm

# i18n
locale.bindtextdomain(APP, LOCALE_DIR)
gettext.bindtextdomain(APP, LOCALE_DIR)
gettext.textdomain(APP)
_ = gettext.gettext

# logger
module_logger = logging.getLogger('LeaptimeManager.appBackup')

# Constants
COL_UUID, COL_NAME, COL_FILENAME, COL_CREATED, COL_REPEAT, COL_LOCATION = range(6)

class AppBackup():
	
	def __init__(self, builder, window, stack, edit_button, browse_button, remove_button) -> None:
		module_logger.info("Initializing App backup module...")
		self.builder = builder
		self.window = window
		self.stack = stack
		self.db_manager = appbackup_db()
		self.backup_manager = AppBackup_backend()
		
		# Acivate action buttons
		self.edit_button = edit_button
		self.browse_button = browse_button
		self.remove_button = remove_button
		
		# Existing backup list treeview
		self.allbackup_tree = self.builder.get_object("treeview_all_appbackup_list")
		# Saved name column
		column = Gtk.TreeViewColumn(_("Name"), Gtk.CellRendererText(), text=COL_NAME)
		column.set_sort_column_id(COL_NAME)
		column.set_resizable(True)
		self.allbackup_tree.append_column(column)
		# Saved file name column
		column = Gtk.TreeViewColumn(_("File Name"), Gtk.CellRendererText(), text=COL_FILENAME)
		column.set_sort_column_id(COL_FILENAME)
		column.set_resizable(True)
		self.allbackup_tree.append_column(column)
		# Created on column
		column = Gtk.TreeViewColumn(_("Created"), Gtk.CellRendererText(), text=COL_CREATED)
		column.set_sort_column_id(COL_CREATED)
		column.set_resizable(True)
		self.allbackup_tree.append_column(column)
		# Repeat job column
		column = Gtk.TreeViewColumn(_("Repeat"), Gtk.CellRendererText(), text=COL_REPEAT)
		column.set_sort_column_id(COL_REPEAT)
		column.set_resizable(True)
		self.allbackup_tree.append_column(column)
		# Save location column
		column = Gtk.TreeViewColumn(_("Location"), Gtk.CellRendererText(), text=COL_LOCATION)
		column.set_sort_column_id(COL_LOCATION)
		column.set_resizable(True)
		self.allbackup_tree.append_column(column)
		
		self.allbackup_tree.show()
		self.model = Gtk.TreeStore(str, str, str, str, str, str)  # uuid, name, filename, created, Repeat, path
		self.model.set_sort_column_id(COL_NAME, Gtk.SortType.ASCENDING)
		self.allbackup_tree.set_model(self.model)
		self.allbackup_tree.get_selection().connect("changed", self.on_appbackup_selected)
		
		# backup packages list treeview
		self.treeview_backup_list = self.builder.get_object("treeview_backup_list")
		self.builder.get_object("button_select").connect("clicked", self.set_selection, self.treeview_backup_list, True, False)
		self.builder.get_object("button_deselect").connect("clicked", self.set_selection, self.treeview_backup_list, False, False)
		tog = Gtk.CellRendererToggle()
		tog.connect("toggled", self.toggled_cb, self.treeview_backup_list)
		c1 = Gtk.TreeViewColumn("", tog, active=0)
		c1.set_cell_data_func(tog, self.celldatamethod_checkbox)
		self.treeview_backup_list.append_column(c1)
		c2 = Gtk.TreeViewColumn("", Gtk.CellRendererText(), markup=2)
		self.treeview_backup_list.append_column(c2)
		
		# File chooser to select existing apps list
		file_filter = Gtk.FileFilter()
		file_filter.add_pattern ("*.list")
		self.restore_filechooser = self.builder.get_object("filechooserbutton_package_source")
		self.restore_filechooser.connect("file-set", self.restore_pkg_validate_file)
		self.restore_filechooser.set_filter(file_filter)
		
		# choose a package list
		self.treeview_restore_list = self.builder.get_object("treeview_restore_list")
		self.builder.get_object("button_select_list").connect("clicked", self.set_selection, self.treeview_restore_list, True, True)
		self.builder.get_object("button_deselect_list").connect("clicked", self.set_selection, self.treeview_restore_list, False, True)
		self.builder.get_object("button_refresh").connect("clicked", self.restore_pkg_load_from_file)
		tog = Gtk.CellRendererToggle()
		tog.connect("toggled", self.toggled_cb, self.treeview_restore_list)
		c1 = Gtk.TreeViewColumn("", tog, active=0, activatable=2)
		c1.set_cell_data_func(tog, self.celldatamethod_checkbox)
		self.treeview_restore_list.append_column(c1)
		c2 = Gtk.TreeViewColumn("", Gtk.CellRendererText(), markup=1)
		self.treeview_restore_list.append_column(c2)
		
		self.selected_appbackup = None
	
	def back_callback(self, widget):
		# Back button
		page = self.stack.get_visible_child_name()
		module_logger.debug("Previous page: %s", page)
		if page == "appbackup_page1" or page == "apprestore_page1":
			# Show App backup main page
			self.load_mainpage()
		elif page == "appbackup_page2":
			# show manually installed packages list page
			self.stack.set_visible_child_name("appbackup_page1")
			self.show_apps_list()
			self.button_back.show()
			self.button_forward.show()
		elif page == "apprestore_page2":
			self.stack.set_visible_child_name("apprestore_page1")
			self.button_back.set_sensitive(True)
			self.button_back.show()
			self.button_forward.show()
			self.button_apply.hide()
		elif page == "apprestore_page3":
			self.stack.set_visible_child_name("apprestore_page2")
			self.button_back.set_sensitive(True)
			self.button_back.show()
			self.button_forward.show()
			self.button_apply.hide()
		
		curr_page = self.stack.get_visible_child_name()
		module_logger.debug("Showing appbackup page: %s on back button", curr_page)
	
	def forward_callback(self, widget):
		# Go forward
		page = self.stack.get_visible_child_name()
		module_logger.debug("Previous page: %s", page)
		self.button_back.set_sensitive(True)
		if page == "appbackup_page1":
			self.stack.set_visible_child_name("appbackup_page2")
			self.button_forward.set_sensitive(True)
			self.button_back.show()
			self.button_forward.show()
		elif page == "appbackup_page2":
			self.backup_name = self.builder.get_object("appbackup_name").get_text()
			self.backup_dest = self.builder.get_object("filechooserbutton_package_dest").get_filename()
			self.backup_pkg_save_to_file()
			self.stack.set_visible_child_name("appbackup_main")
			self.button_back.hide()
			self.button_forward.hide()
			self.load_mainpage()
		elif page == "apprestore_page1":
			self.stack.set_visible_child_name("apprestore_page2")
			self.button_back.show()
			self.button_forward.hide()
			self.button_apply.show()
			self.restore_pkg_load_from_file(widget)
		elif page == "apprestore_page2":
			inst = False
			model = self.treeview_restore_list.get_model()
			if len(model) == 0:
				show_message(self.window, _("No packages need to be installed."))
				return
			for row in model:
				if row[0]:
					inst = True
					break
			if not inst:
				show_message(self.window, _("No packages selected to install."))
				return
			else:
				self.restore_pkg_install_packages()
			if inst:
				self.stack.set_visible_child_name("apprestore_page3")
				self.button_back.show()
				self.button_apply.hide()
				self.button_forward.show()
		elif page == "apprestore_page3":
			self.stack.set_visible_child_name("appbackup_main")
			self.button_back.set_sensitive(False)
			self.button_back.hide()
			self.button_forward.hide()
			self.load_mainpage()
		
		page = self.stack.get_visible_child_name()
		module_logger.debug("Showing appbackup page: %s on forward button", page)
	
	def toggled_cb(self, ren, path, treeview):
		model = treeview.get_model()
		iter = model.get_iter(path)
		if iter != None:
			checked = model.get_value(iter, 0)
			model.set_value(iter, 0, (not checked))
	
	def celldatamethod_checkbox(self, column, cell, model, iter, app_list):
		checked = model.get_value(iter, 0)
		cell.set_property("active", checked)
	
	def set_selection(self, w, treeview, selection, check):
		# Select / deselect all
		model = treeview.get_model()
		for row in model:
			if check:
				if row[2]:
					row[0] = selection
			else:
				row[0] = selection
	
	def backup_pkg_save_to_file(self):
		if self.backup_dest is not None:
			self.backup_manager.pkg_backup_save_to_file(self.backup_name, self.backup_dest, self.cache)
		else:
			show_message(self.window, _("No backup destination is selected."))
			self.stack.set_visible_child_name("appbackup_page2")
			self.button_forward.set_sensitive(True)
			self.button_back.show()
			self.button_forward.show()
	
	def show_apps_list(self):
		# Update apt cache
		apt_pkg.init()
		self.cache = apt_pkg.Cache()					# all cache packages
		module_logger.debug(_("Showing manually installed apps list..."))
		model = Gtk.ListStore(bool, str, str)
		model.set_sort_column_id(1, Gtk.SortType.ASCENDING)
		
		try:
			installed_pkg_list = self.backup_manager.create_installed_pkg_list(self.cache)
			for item in installed_pkg_list:
				model.append(item)
			self.treeview_backup_list.set_model(model)
			self.stack.set_visible_child_name("appbackup_page1")
			self.button_back.set_sensitive(True)
			self.button_back.show()
			self.button_forward.show()
		except Exception as e:
			print(e)
			show_message(self.window, _("Could not get manually installed packages. Check logs for more details."))
			self.stack.set_visible_child_name("appbackup_main")
			self.button_back.hide()
			self.button_forward.hide()
			self.load_mainpage()
	
	def restore_pkg_validate_file(self, filechooser):
		self.backup_src = filechooser.get_filename()
		# Check the file validity
		try:
			with open(self.backup_src, "r") as source:
				for line in source:
					line = line.rstrip("\r\n")
					if line != "":
						if not line.endswith("\tinstall") and not line.endswith(" install"):
							show_message(self.window, _("The selected file is not a valid software selection."))
							self.button_forward.set_sensitive(False)
							return
			module_logger.debug(_("Validation passed for restore file: %s" % self.backup_src))
			self.button_forward.set_sensitive(True)
		except Exception as detail:
			show_message(self.window, _("An error occurred while reading the file."))
			module_logger.debug(detail)
	
	def restore_pkg_load_from_file(self, widget=None):
		# Load package list into treeview
		apt_pkg.init()
		self.cache = apt_pkg.Cache()					# all cache packages
		self.button_forward.hide()
		self.button_apply.show()
		self.button_apply.set_sensitive(True)
		model = Gtk.ListStore(bool, str, bool, str)
		self.treeview_restore_list.set_model(model)
		try:
			with open(self.backup_src, "r") as f:
				source = f.readlines()
			package_records = apt_pkg.PackageRecords(self.cache)
			depcache = apt_pkg.DepCache(self.cache)
			for line in source:
				try:
					if not line.strip() or line.startswith("#"):
						continue
					name = line.strip().replace(" install", "").replace("\tinstall", "")
					if not name:
						continue
					error = "%s\n<small>%s</small>" % (name, _("Could not locate the package."))
					if name in self.cache:
						pkg = self.cache[name]
						if not pkg.current_ver:
							candidate = depcache.get_candidate_ver(pkg)
							if candidate and candidate.downloadable:
								package_records.lookup(candidate.translated_description.file_list[0])
								summary = package_records.short_desc
								status = "%s\n<small>%s</small>" % (name, GLib.markup_escape_text(summary))
								model.append([True, status, True, pkg.name])
							else:
								model.append([False, error, False, pkg.name])
					else:
						model.append([False, error, False, error])
				except Exception as inner_detail:
					print("Error while reading '%s'." % line.strip())
					print(inner_detail)
		except Exception as detail:
			show_message(self.window, _("An error occurred while reading the file."))
			print (detail)
		if len(model) == 0:
			self.stack.set_visible_child_name("apprestore_page3")
			self.button_forward.show()
			self.button_back.hide()
			self.button_apply.hide()
		else:
			self.button_back.show()
			self.stack.set_visible_child_name("apprestore_page2")
	
	def apt_run_transaction(self, transaction):
		transaction.connect("finished", self.on_transaction_finish)
		dia = AptProgressDialog(transaction, parent=self.window)
		dia.run(close_on_finished=True, show_error=True, reply_handler=lambda: True, error_handler=self.apt_on_error)
	
	def apt_simulate_trans(self, trans):
		trans.simulate(reply_handler=lambda: self.apt_confirm_deps(trans), error_handler=self.apt_on_error)
	
	def apt_confirm_deps(self, trans):
		try:
			if [pkgs for pkgs in trans.dependencies if pkgs]:
				dia = AptConfirmDialog(trans, parent=self.window)
				res = dia.run()
				dia.hide()
				if res != Gtk.ResponseType.OK:
					return
			self.apt_run_transaction(trans)
		except Exception as e:
			print(e)
	
	def apt_on_error(self, error):
		if isinstance(error, aptdaemon.errors.NotAuthorizedError):
			# Silently ignore auth failures
			return
		elif not isinstance(error, aptdaemon.errors.TransactionFailed):
			# Catch internal errors of the client
			error = aptdaemon.errors.TransactionFailed(ERROR_UNKNOWN, str(error))
		dia = AptErrorDialog(error)
		dia.run()
		dia.hide()
	
	def on_transaction_finish(self, transaction, exit_state):
		# Refresh
		self.restore_pkg_load_from_file()
	
	def restore_pkg_install_packages(self):
		packages = []
		model = self.treeview_restore_list.get_model()
		for row in model:
			if row[0]:
				packages.append(row[3])
		ac = aptdaemon.client.AptClient()
		ac.install_packages(packages, reply_handler=self.apt_simulate_trans, error_handler=self.apt_on_error)
	
	# Stack pages load functions
	def load_mainpage(self):
		module_logger.debug(_("Loading main page with available backups lists."))
		# Clear treeview and selection
		self.app_db_list = self.db_manager.read_db()
		self.backup_manager.back_compat()
		module_logger.debug(_("Existing app backups: %s" % self.app_db_list))
		self.stack.set_visible_child_name("appbackup_main")
		self.button_back.set_sensitive(False)
		self.button_back.hide()
		self.button_forward.hide()
		self.model.clear()
		for backup in self.app_db_list:
			iter = self.model.insert_before(None, None)
			self.model.set_value(iter, COL_UUID, backup["uuid"])
			self.model.set_value(iter, COL_NAME, backup["name"])
			self.model.set_value(iter, COL_FILENAME, backup["filename"])
			self.model.set_value(iter, COL_CREATED, backup["created"])
			self.model.set_value(iter, COL_REPEAT, backup["repeat"])
			self.model.set_value(iter, COL_LOCATION, backup["location"])
	
	def on_appbackup_selected(self, selection):
		model, iter = selection.get_selected()
		if iter is not None:
			self.selected_appbackup = model.get_value(iter, COL_UUID)
			module_logger.debug(_("Selected app backup: %s" % self.selected_appbackup))
			self.edit_button.set_sensitive(True)
			self.browse_button.set_sensitive(True)
			self.remove_button.set_sensitive(True)
	
	def reload_nav_btns(self, button_back, button_forward, button_apply, app_backup=False):
		module_logger.debug(_("Reloading navigation buttons for app backup."))
		# nav buttons
		self.button_back = button_back
		self.button_forward = button_forward
		self.button_apply = button_apply
		
		if app_backup:
			self.button_back.connect("clicked", self.back_callback)
			self.button_forward.connect("clicked", self.forward_callback)
			self.button_apply.connect("clicked", self.forward_callback)
	
	# Main button definitions
	def on_backup_apps(self, widget):
		# On add button press
		module_logger.debug(_("Starting app backup list process"))
		# show manually installed packages list page
		self.show_apps_list()
	
	def on_restore_apps(self, widget):
		# On restore button press
		module_logger.debug(_("Starting app restore list process"))
		self.stack.set_visible_child_name("apprestore_page1")
		self.button_back.set_sensitive(True)
		self.button_forward.set_sensitive(False)
		# restore from backup file
		for i in range(len(self.app_db_list)):
			if self.app_db_list[i]['uuid'] == self.selected_appbackup:
				backup_dict = self.app_db_list[i]
				backup_filepath = os.path.join(backup_dict["location"], backup_dict["filename"])
				module_logger.debug(_("Restoring from file: %s" % backup_filepath))
				self.restore_filechooser.set_filename(backup_filepath)
				self.restore_pkg_validate_file(self.restore_filechooser)
		self.button_back.show()
		self.button_forward.show()
		self.button_apply.hide()
	
	def on_edit_appbackup(self, widget):
		# On edit button press
		module_logger.debug(_("Editing backup file from database list."))
		show_message(self.window, _("This feature has not been implented yet. Please wait for future releases."))
	
	def on_browse_appbackup(self, widget):
		# On browse button press
		module_logger.debug(_("Opening directory of backup file from database list."))
		# Open directory of backup file
		for i in range(len(self.app_db_list)):
			if self.app_db_list[i]['uuid'] == self.selected_appbackup:
				backup_dict = self.app_db_list[i]
				subprocess.Popen(['xdg-open', backup_dict["location"]])
	
	def on_remove_appbackup(self, widget):
		# On remove button press
		module_logger.debug(_("Removing app backup from database list."))
		# remove app backup
		for i in range(len(self.app_db_list)):
			if self.app_db_list[i]['uuid'] == self.selected_appbackup:
				backup_dict = self.app_db_list[i]
				backup_filepath = os.path.join(backup_dict["location"], backup_dict["filename"])
				
				msg = "app backup"
				msg_detail = backup_dict["name"]
				if delete_confirm(self.window, msg, msg_detail):
					# Remove the backup file
					try:
						os.remove(backup_filepath)
						module_logger.info(_(f"Removed app backup file: {backup_filepath}"))
					except OSError as e:
						# Log the error but continue to remove the entry from the DB list
						module_logger.error(_(f"Error removing file {backup_filepath}: {e.strerror}"))
					# remove entry from database
					del self.app_db_list[i]
					module_logger.info(_(f"{msg} '{msg_detail}' removed from database list."))
					break
		
		# Write the modified list back to the database file
		self.db_manager.write_db(self.app_db_list)
		
		self.load_mainpage()
