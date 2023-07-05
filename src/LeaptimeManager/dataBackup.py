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
from LeaptimeManager.common import APP, LOCALE_DIR, DATA_LOG_DIR
from LeaptimeManager.database_rw import databackup_db
from LeaptimeManager.dialogs import show_message

# i18n
locale.bindtextdomain(APP, LOCALE_DIR)
gettext.bindtextdomain(APP, LOCALE_DIR)
gettext.textdomain(APP)
_ = gettext.gettext

# logger
module_logger = logging.getLogger('LeaptimeManager.dataBackup')

# Constants
COL_NAME, COL_METHOD, COL_SOURCE, COL_DESTINATION, COL_CREATED, COL_REPEAT, COL_COMMENT = range(7)
META_FILE = ".meta"

class UserData_backend():
	
	def __init__(self) -> None:
		module_logger.info("Initializing User Data backend class...")

class UserData():
	"""
	GUI class for backing up and restoring user data
	using rsync
	"""
	def __init__(self, builder, window, stack, button_back, button_forward, button_apply) -> None:
		module_logger.info(_("Initializing user data backup class..."))
		self.builder = builder
		self.window = window
		self.stack = stack
		self.db_manager = databackup_db()
		# inidicates whether an operation is taking place.
		self.operating = False
		self.backup_name = ""
		
		# nav buttons
		self.button_back = button_back
		self.button_forward = button_forward
		self.button_apply = button_apply
		
		self.button_back.connect("clicked", self.back_callback)
		self.button_forward.connect("clicked", self.forward_callback)
		self.button_apply.connect("clicked", self.forward_callback)
		
		# entries
		self.backup_name_entry = self.builder.get_object("data_backup_name")
		self.backup_desc_entry = self.builder.get_object("data_backup_comment")
		
		# Existing backup list treeview
		self.allbackup_tree = self.builder.get_object("treeview_all_databackup_list")
		# Name column
		column = Gtk.TreeViewColumn(_("Name"), Gtk.CellRendererText(), text=COL_NAME)
		column.set_sort_column_id(COL_NAME)
		column.set_resizable(True)
		self.allbackup_tree.append_column(column)
		# Method column
		column = Gtk.TreeViewColumn(_("Method"), Gtk.CellRendererText(), text=COL_METHOD)
		column.set_sort_column_id(COL_METHOD)
		column.set_resizable(True)
		self.allbackup_tree.append_column(column)
		# Source column
		column = Gtk.TreeViewColumn(_("Source"), Gtk.CellRendererText(), text=COL_SOURCE)
		column.set_sort_column_id(COL_SOURCE)
		column.set_resizable(True)
		self.allbackup_tree.append_column(column)
		# Destination column
		column = Gtk.TreeViewColumn(_("Destination"), Gtk.CellRendererText(), text=COL_DESTINATION)
		column.set_sort_column_id(COL_DESTINATION)
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
		# Comment column
		column = Gtk.TreeViewColumn(_("Comment"), Gtk.CellRendererText(), text=COL_COMMENT)
		column.set_sort_column_id(COL_COMMENT)
		column.set_resizable(True)
		self.allbackup_tree.append_column(column)
		
		self.allbackup_tree.show()
		self.model = Gtk.TreeStore(str, str, str, str, str, str, str)  # name, method, source, destination, created, repeat, comment
		self.model.set_sort_column_id(COL_NAME, Gtk.SortType.ASCENDING)
		self.allbackup_tree.set_model(self.model)
		
		# Select source
		filechooser_src = self.builder.get_object("filechooserbutton_backup_source")
		filechooser_src.connect("file-set", self.on_select_src)
		
		# Select destination
		filechooser_dest = self.builder.get_object("filechooserbutton_backup_dest")
		filechooser_dest.connect("file-set", self.on_select_dest)
		
		# Combo box
		self.methods_combo = self.builder.get_object("methods_combo")
		self.methods_combo.set_active(0)
		self.methods_combo.connect("changed", self.method_combo_changed)
		
		# tarball combo
		self.tarballs_combo = self.builder.get_object("tar_format_combo")
		self.tarballs_combo.set_active(0)
		self.tarballs_combo.connect("changed", self.tar_format_combo_changed)
		
	def back_callback(self, widget):
		# Back button
		page = self.stack.get_visible_child_name()
		module_logger.debug("Previous page: %s", page)
		if page == "databackup_page1" or page == "datarestore_page1":
			# Show App backup main page
			self.load_mainpage()
		
		page = self.stack.get_visible_child_name()
		module_logger.debug("Showing databackup page: %s on back button", page)
	
	def forward_callback(self, widget):
		# Go forward
		page = self.stack.get_visible_child_name()
		module_logger.debug("Previous page: %s", page)
		self.builder.get_object("button_back").set_sensitive(True)
		
		page = self.stack.get_visible_child_name()
		module_logger.debug("Showing databackup page: %s on forward button", page)
	
	def on_select_src(self, filechooser):
		self.source_dir = filechooser.get_filename()
	
	def on_select_dest(self, filechooser):
		self.dest_dir = filechooser.get_filename()
	
	def tar_format_combo_changed(self, combotext):
		self.tar_backup_format = combotext.get_active_text()
		print(self.tar_backup_format)
	
	def method_combo_changed(self, combotext):
		self.backup_method = combotext.get_active_text()
		if self.backup_method == "rsync":
			self.builder.get_object("tar_format_label").set_visible(False)
			self.builder.get_object("tar_format_combo").set_visible(False)
		else:
			self.builder.get_object("tar_format_label").set_visible(True)
			self.builder.get_object("tar_format_combo").set_visible(True)
			# show_message(self.window, _("This feature has not been implented yet. Use rsync method."))
	
	def on_treeview_excludes_selection_changed(self, selection):
		liststore, treeiter = selection.get_selected()
		self.builder.get_object("button_remove_exclude").set_sensitive((treeiter and liststore.get_value(treeiter, 2) != self.dest_dir))
	
	def add_item_to_treeview(self, widget, treeview, icon, mode, show_hidden=False):
		# Add a file or directory to treeview
		dialog = Gtk.FileChooserDialog(title=("Backup Tool"), parent=self.main_window, action=mode)
		dialog.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OPEN, Gtk.ResponseType.OK)
		dialog.set_current_folder(self.source_dir)
		dialog.set_select_multiple(True)
		dialog.set_show_hidden(show_hidden)
		if dialog.run() == Gtk.ResponseType.OK:
			filenames = dialog.get_filenames()
			for filename in filenames:
				if not filename.find(self.source_dir):
					found = False
					model = treeview.get_model()
					for row in model:
						if row[2] == filename:
							found = True
					if not found:
						treeview.get_model().append([filename[len(self.source_dir) + 1:], icon, filename])
				else:
					self.show_message(_("%s is not located in your source directory.") % filename)
		dialog.destroy()
	
	def remove_item_from_treeview(self, button, treeview):
		# Remove the item from the treeview
		model = treeview.get_model()
		selection = treeview.get_selection()
		selected_rows = selection.get_selected_rows()[1]
		args = [(model.get_iter(path)) for path in selected_rows]
		for iter in args:
			model.remove(iter)
	
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
			if not self.dest_dir:
				module_logger.error("No destination directory selected.")
	
	
	def load_mainpage(self):
		module_logger.debug(_("Loading main page with available data backups lists."))
		# Clear treeview and selection
		self.data_db_list = self.db_manager.read_db()
		module_logger.debug(_("Existing data backups: %s" % self.data_db_list))
		self.stack.set_visible_child_name("databackup_main")
		self.model.clear()
		for backup in self.data_db_list:
			iter = self.model.insert_before(None, None)
			self.model.set_value(iter, COL_NAME, backup["name"])
			self.model.set_value(iter, COL_METHOD, backup["method"])
			self.model.set_value(iter, COL_SOURCE, backup["source"])
			self.model.set_value(iter, COL_DESTINATION, backup["destination"])
			self.model.set_value(iter, COL_CREATED, backup["created"])
			self.model.set_value(iter, COL_REPEAT, backup["repeat"])
			self.model.set_value(iter, COL_COMMENT, backup["comment"])
		self.button_back.set_sensitive(False)
		self.button_back.hide()
		self.button_forward.hide()
		self.button_apply.hide()

	def on_backup_selected(self, selection):
		model, iter = selection.get_selected()
		if iter is not None:
			self.selected_webapp = model.get_value(iter, COL_NAME)
			self.remove_button.set_sensitive(True)
			self.edit_button.set_sensitive(True)
	
	def on_backup_data(self, widget):
		module_logger.info("Starting Data backup...")
		self.stack.set_visible_child_name("databackup_page1")
		self.button_back.set_sensitive(True)
		self.button_back.show()
		self.button_forward.show()
	
	def on_restore_data(self, widget):
		module_logger.info("Starting Data restore...")
		self.button_back.set_sensitive(True)
		self.button_back.show()
		self.button_forward.show()
		show_message(self.window, _("This feature has not been implented yet. Please wait for future releases."))
