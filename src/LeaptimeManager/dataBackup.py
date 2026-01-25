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
import gi
import glob
import locale
import logging
import os
import shutil
import subprocess


gi.require_version("Gtk", "3.0")
gi.require_version("XApp", "1.0")
from gi.repository import GLib, GdkPixbuf, Gtk, XApp

# imports from current package
from LeaptimeManager.cli_args import  APP, LOCALE_DIR
from LeaptimeManager.common import _async, _print_timing
from LeaptimeManager.database_rw import databackup_db
from LeaptimeManager.dialogs import show_message, delete_confirm
from LeaptimeManager.scheduler import TimeChooserButton
from LeaptimeManager.dataBackup_backend import UserData_backend
from LeaptimeManager.tarball_backend import tar_backend

# i18n
locale.bindtextdomain(APP, LOCALE_DIR)
gettext.bindtextdomain(APP, LOCALE_DIR)
gettext.textdomain(APP)
_ = gettext.gettext

# logger
module_logger = logging.getLogger('LeaptimeManager.dataBackup')

# Constants
COL_UUID, COL_NAME, COL_METHOD, COL_SOURCE, COL_DESTINATION, COL_CREATED, COL_REPEAT, COL_COMMENT = range(8)


class UserData():
	"""
	GUI class for backing up and restoring user data
	using tarball or rsync
	"""
	def __init__(self, builder, window, stack, edit_button, browse_button, remove_button) -> None:
		module_logger.info(_("Initializing user data backup class..."))
		self.builder = builder
		self.window = window
		self.stack = stack
		self.db_manager = databackup_db()
		
		# Acivate action buttons
		self.edit_button = edit_button
		self.browse_button = browse_button
		self.remove_button = remove_button
		
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
		self.model = Gtk.TreeStore(str, str, str, str, str, str, str, str)  # uuid, name, method, source, destination, created, repeat, comment
		self.model.set_sort_column_id(COL_NAME, Gtk.SortType.ASCENDING)
		self.allbackup_tree.set_model(self.model)
		self.allbackup_tree.get_selection().connect("changed", self.on_backup_selected)
		
		# Select source
		filechooser_src = self.builder.get_object("filechooserbutton_backup_source")
		filechooser_src.connect("file-set", self.on_select_src)
		
		# Select destination
		filechooser_dest = self.builder.get_object("filechooserbutton_backup_dest")
		filechooser_dest.connect("file-set", self.on_select_dest)
		
		# Mode Combo box
		self.backup_mode_combo = self.builder.get_object("backup_mode_combo")
		self.backup_mode_combo.set_active(0)
		self.backup_mode_combo.connect("changed", self.mode_combo_changed)
		
		# Combo box
		self.methods_combo = self.builder.get_object("methods_combo")
		self.methods_combo.set_active(0)
		self.methods_combo.connect("changed", self.method_combo_changed)
		
		# tarball combo
		self.tarballs_combo = self.builder.get_object("tar_format_combo")
		self.tarballs_combo.set_active(0)
		self.tarballs_combo.connect("changed", self.tar_format_combo_changed)
		
		# Schedule radio button
		self.specific_time_btn = self.builder.get_object("specific_time_btn")
		self.specific_time_btn.connect("toggled", self.toggled_schedule_btn)
		self.specific_time_box = self.builder.get_object("specific_time_box")
		self.backup_time_btn = TimeChooserButton()
		self.specific_time_box.pack_start(self.backup_time_btn, False, False, 0)
		self.specific_interval_btn = self.builder.get_object("specific_interval_btn")
		self.specific_interval_btn.connect("toggled", self.toggled_schedule_btn)
		
		# set up exclusions page
		self.iconTheme = Gtk.IconTheme.get_default()
		self.dir_icon = self.iconTheme.load_icon("folder-symbolic", 16, 0)
		self.file_icon = self.iconTheme.load_icon("folder-documents-symbolic", 16, 0)
		treeview = self.builder.get_object("treeview_excludes")
		renderer = Gtk.CellRendererPixbuf()
		column = Gtk.TreeViewColumn("", renderer)
		column.add_attribute(renderer, "pixbuf", 1)
		treeview.append_column(column)
		renderer = Gtk.CellRendererText()
		column = Gtk.TreeViewColumn("", renderer)
		column.add_attribute(renderer, "text", 0)
		treeview.append_column(column)
		self.excludes_model = Gtk.ListStore(str, GdkPixbuf.Pixbuf, str)
		self.excludes_model.set_sort_column_id(0, Gtk.SortType.ASCENDING)
		treeview.set_model(self.excludes_model)
		self.builder.get_object("button_add_file").connect("clicked", self.add_item_to_treeview, treeview, self.file_icon, Gtk.FileChooserAction.OPEN, False)
		self.builder.get_object("button_add_folder").connect("clicked", self.add_item_to_treeview, treeview, self.dir_icon, Gtk.FileChooserAction.SELECT_FOLDER, False)
		self.builder.get_object("button_remove_exclude").connect("clicked", self.remove_item_from_treeview, treeview)
		self.builder.get_object("treeview_excludes_selection").connect("changed", self.on_treeview_excludes_selection_changed)
		
		# set up inclusions page
		treeview = self.builder.get_object("treeview_includes")
		renderer = Gtk.CellRendererPixbuf()
		column = Gtk.TreeViewColumn("", renderer)
		column.add_attribute(renderer, "pixbuf", 1)
		treeview.append_column(column)
		renderer = Gtk.CellRendererText()
		column = Gtk.TreeViewColumn('', renderer)
		column.add_attribute(renderer, "text", 0)
		treeview.append_column(column)
		self.includes_model = Gtk.ListStore(str, GdkPixbuf.Pixbuf, str)
		self.includes_model.set_sort_column_id(0, Gtk.SortType.ASCENDING)
		treeview.set_model(self.includes_model)
		self.builder.get_object("button_include_hidden_files").connect("clicked", self.add_item_to_treeview, treeview, self.file_icon, Gtk.FileChooserAction.OPEN, True)
		self.builder.get_object("button_include_hidden_dirs").connect("clicked", self.add_item_to_treeview, treeview, self.dir_icon, Gtk.FileChooserAction.SELECT_FOLDER, True)
		self.builder.get_object("button_remove_include").connect("clicked", self.remove_item_from_treeview, treeview)
		
		# Progressbars
		self.progressbar = self.builder.get_object("progressbar1")
		# Errors treeview for backup
		ren = Gtk.CellRendererText()
		column = Gtk.TreeViewColumn("", ren)
		column.add_attribute(ren, "text", 0)
		self.builder.get_object("treeview_backup_errors").append_column(column)
		column = Gtk.TreeViewColumn("", ren)
		column.add_attribute(ren, "text", 1)
		self.builder.get_object("treeview_backup_errors").append_column(column)
		
		self.errors = Gtk.ListStore(str, str)
		
		# Backend managers
		self.manager = UserData_backend(self.errors)
		self.tar_manager = tar_backend(self.errors)
	
	def back_callback(self, widget):
		# Back button
		page = self.stack.get_visible_child_name()
		module_logger.debug(_("Previous page: %s"), page)
		
		if page == "databackup_page1" or page == "datarestore_page1":
			# Show App backup main page
			self.load_mainpage()
		elif page == "databackup_page2":
			# show page 1 of data backup
			self.stack.set_visible_child_name("databackup_page1")
			self.backup_name_entry.set_text(self.backup_name)
			self.backup_desc_entry.set_text(self.backup_desc)
		elif page == "databackup_page3":
			# show page 2 (excludes page) of data backup
			self.stack.set_visible_child_name("databackup_page2")
			self.button_forward.show()
			self.button_apply.hide()
			# Cannot be returned from backup page 4 and 5
			# So, no back button for page 4 and 5
		
		page = self.stack.get_visible_child_name()
		module_logger.debug(_("Showing databackup page: %s on back button"), page)
	
	def forward_callback(self, widget):
		# Go forward
		page = self.stack.get_visible_child_name()
		module_logger.debug(_("Previous page: %s"), page)
		self.button_back.set_sensitive(True)
		if page == "databackup_page1":
			# Gather info from page 1
			self.prep_backup()
			# show page 2 of data backup
			self.stack.set_visible_child_name("databackup_page2")
		elif page == "databackup_page2":
			# Gather info from page 2
			self.calculate_excludes()
			# show page 3 (includes page) of data backup
			self.stack.set_visible_child_name("databackup_page3")
			self.button_forward.hide()
			self.button_apply.show()
			self.button_apply.set_label(_("Start Backup"))
		elif page == "databackup_page3":
			# Gather info from page 3
			self.calculate_includes()
			# show page 4 of data backup
			self.stack.set_visible_child_name("databackup_page4")
			self.button_back.hide()
			self.button_apply.hide()
			# start the actual backup in another thread
			_async(self.backup_data)()
		elif page == "databackup_page4":
			# show page 5 of data backup
			self.stack.set_visible_child_name("databackup_page5")
			self.button_forward.hide()
			self.button_apply.show()
			self.button_apply.set_label(_("Finish"))
		elif page == "databackup_page5":
			# show main page of data backup
			self.stack.set_visible_child_name("databackup_main")
			self.load_mainpage()
		
		curr_page = self.stack.get_visible_child_name()
		module_logger.debug(_("Showing databackup page: %s on forward button"), curr_page)
	
	def on_select_src(self, filechooser):
		self.source_dir = filechooser.get_filename()
	
	def on_select_dest(self, filechooser):
		self.dest_dir = filechooser.get_filename()
	
	def mode_combo_changed(self, combotext):
		self.backup_mode = combotext.get_active_text().lower()
		module_logger.debug(_("Using backup mode: %s"),self.backup_mode)
		if self.backup_mode == "backup":
			pass
		else:
			show_message(self.window, _("This feature has not been implented yet. Please wait for future releases."))
			self.backup_mode_combo.set_active(0)
	
	def tar_format_combo_changed(self, combotext):
		self.tar_backup_format = combotext.get_active_text()
		module_logger.debug(_("Tarball format for backup: %s"),self.tar_backup_format)
	
	def method_combo_changed(self, combotext):
		self.backup_method = combotext.get_active_text()
		module_logger.debug(_("Using backup method: %s"),self.backup_method)
		if self.backup_method == "rsync":
			self.builder.get_object("tar_format_label").set_visible(False)
			self.builder.get_object("tar_format_combo").set_visible(False)
		else:
			self.builder.get_object("tar_format_label").set_visible(True)
			self.builder.get_object("tar_format_combo").set_visible(True)
	
	def toggled_schedule_btn(self, button):
		if self.specific_time_btn.get_active():
			self.builder.get_object("specific_time_box").set_visible(True)
			self.builder.get_object("specific_interval_grid").set_visible(False)
		elif self.specific_interval_btn.get_active():
			self.builder.get_object("specific_time_box").set_visible(False)
			self.builder.get_object("specific_interval_grid").set_visible(True)
	
	def on_treeview_excludes_selection_changed(self, selection):
		liststore, treeiter = selection.get_selected()
		self.builder.get_object("button_remove_exclude").set_sensitive((treeiter and liststore.get_value(treeiter, 2) != self.dest_dir))
	
	def add_item_to_treeview(self, widget, treeview, icon, mode, show_hidden=False):
		# Add a file or directory to treeview
		if mode == Gtk.FileChooserAction.OPEN:
			title= _("Data Backup - Select files")
		else:
			title= _("Data Backup - Select folders")
		dialog = Gtk.FileChooserDialog(title=title, parent=self.window, action=mode)
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
	
	def prep_backup(self):
		module_logger.debug(_("Gathering info on backup."))
		self.backup_name = self.backup_name_entry.get_text()
		self.backup_desc = self.backup_desc_entry.get_text()
		self.backup_method = self.methods_combo.get_active_text()
		try:
			if self.source_dir and self.dest_dir and os.access(self.dest_dir, os.W_OK):
				module_logger.debug(_(f"Name: {self.backup_name}, Description: {self.backup_desc}, Source: {self.source_dir}, Destination: {self.dest_dir}, Method: {self.backup_method}"))
				if self.backup_method == "tarball":
					self.tar_backup_format = self.tarballs_combo.get_active_text()
					module_logger.debug(_("Tar archive format: %s") % self.tar_backup_format)
		except Exception as e:
			module_logger.error(e)
			if not self.source_dir:
				module_logger.error(_("No source directory selected."))
				self.show_message(_("No source directory selected."))
			if not self.dest_dir:
				module_logger.error(_("No destination directory selected."))
				self.show_message(_("No destination directory selected."))
			if not os.access(self.dest_dir, os.W_OK):
				self.show_message(_("You do not have the permission to write in the selected destination directory."))
	
	def calculate_excludes(self):
		# Calculate excludes
		self.excluded_dirs = []
		self.excluded_files = []
		for row in self.excludes_model:
			item = row[2]
			if os.path.exists(item):
				if os.path.isdir(item):
					self.excluded_dirs.append(item)
				else:
					self.excluded_files.append(item)
		module_logger.debug(_("Excluded files list: %s") % self.excluded_files)
		module_logger.debug(_("Excluded folder list: %s") % self.excluded_dirs)
	
	def calculate_includes(self):
		# Calculate includes
		self.included_dirs = []
		self.included_files = []
		for row in self.includes_model:
			item = row[2]
			if os.path.exists(item):
				if os.path.isdir(item):
					self.included_dirs.append(item)
				else:
					self.included_files.append(item)
		module_logger.debug(_("Included files list: %s") % self.included_files)
		module_logger.debug(_("Included folder list: %s") % self.included_dirs)
	
	def set_progress(self, archived_file_size, total_size, backuplog):
		fraction = float(archived_file_size) / float(total_size)
		int_fraction = int(fraction * 100)
		self.progressbar.set_fraction(fraction)
		self.progressbar.set_text(str(int_fraction) + "%")
		self.logview = self.builder.get_object("databackup_log_view")
		self.logview.set_editable(False)
		self.logview.set_wrap_mode(Gtk.WrapMode.WORD)
		self.logview.get_buffer().set_text(backuplog)
		XApp.set_window_progress(self.window, int_fraction)
	
	def set_widgets_before_backup(self):
		self.builder.get_object("button_apply").hide()
		self.builder.get_object("button_forward").hide()
		self.builder.get_object("button_back").hide()
		self.progressbar.set_text(_("Calculating..."))
	
	def set_widgets_after_backup(self):
		if len(self.errors) > 0:
			self.builder.get_object("label_finished_status").set_markup(_("The following errors occurred:"))
			self.builder.get_object("image_finished").set_from_icon_name("dialog-error-symbolic", Gtk.IconSize.DIALOG)
			self.builder.get_object("treeview_backup_errors").set_model(self.errors)
			self.builder.get_object("win_errors").show_all()
		else:
			if not self.tar_manager.operating:
				self.builder.get_object("label_finished_status").set_markup(_("The backup was aborted."))
				self.builder.get_object("image_finished").set_from_icon_name("dialog-warning-symbolic", Gtk.IconSize.DIALOG)
			else:
				self.builder.get_object("image_finished").set_from_icon_name("success-symbolic", Gtk.IconSize.DIALOG)
				self.builder.get_object("label_finished_status").set_markup(_("Your files were successfully saved in %s.") % self.tarfilename)
		self.button_forward.show()
		self.tar_manager.operating = False
		self.progressbar.set_fraction(1.0)
		self.progressbar.set_text(str(100) + "%")
		XApp.set_window_progress(self.window, 0)
	
	def tar_backup(self):
		# Does the actual copying
		try:
			self.timestamp, self.tarfilename, self.num_files, self.total_size, copy_files = self.tar_manager.prep_tar_backup(self.backup_name, self.source_dir, self.dest_dir, self.excluded_files, self.excluded_dirs, self.included_files, self.included_dirs, self.tar_backup_format)
			
			self.tar_manager.add_meta_tar_backup()
			
			archived_files = 0
			self.archived_file_size = 0
			self.backuplog = ""
			for path in copy_files:
				archived_files, self.archived_file_size, backuplog = self.tar_manager.callback_add_to_tar(path, archived_files, self.archived_file_size)
				self.backuplog += backuplog
				GLib.idle_add(self.set_progress, self.archived_file_size, self.total_size, self.backuplog)
			self.tar_manager.finish_tar_backup(self.backuplog, self.backup_desc, self.backup_method)
		except Exception as e:
			print(e)
	
	@_print_timing
	def backup_data(self):
		GLib.idle_add(self.set_widgets_before_backup)
		if self.backup_method == "rsync":
			module_logger.info(_("Starting backup using Rsync method..."))
			show_message(self.window, _("This feature has not been implented yet. Use tarball method."))
			# cmd = "rsync -aAXUH --checksum --compress --partial --progress %s %s" % (self.source_dir, self.dest_dir)
			# cmd = list(cmd.split(" "))
			# module_logger.debug(_("Running command: %s") % cmd)
			# with open(self.backuplog, "a") as logfile:
			# 	subprocess.Popen(cmd, shell=False, stdout=logfile)
			module_logger.info(_("%s is backed up into %s") % (self.source_dir, self.dest_dir))
		else:
			module_logger.info(_("Starting backup using tarball method..."))
			self.tar_backup()
			module_logger.info(_("%(source_dir)s is backed up into %(tarfile)s" % {'source_dir': self.source_dir, 'tarfile': self.tarfilename}))
		
		GLib.idle_add(self.set_widgets_after_backup)
	
	# Page load definition functions
	def load_mainpage(self):
		module_logger.debug(_("Loading main page with available data backups lists."))
		# Clear treeview and selection
		self.data_db_list = self.db_manager.read_db()
		self.manager.back_compat(self.window)
		module_logger.debug(_("Existing data backups: %s" % self.data_db_list))
		self.stack.set_visible_child_name("databackup_main")
		self.model.clear()
		for backup in self.data_db_list:
			iter = self.model.insert_before(None, None)
			self.model.set_value(iter, COL_UUID, backup["uuid"])
			self.model.set_value(iter, COL_NAME, backup["name"])
			self.model.set_value(iter, COL_METHOD, backup["method"])
			self.model.set_value(iter, COL_SOURCE, backup["source"])
			self.model.set_value(iter, COL_DESTINATION, backup["destination"])
			self.model.set_value(iter, COL_CREATED, backup["created"])
			self.model.set_value(iter, COL_REPEAT, str(backup["repeat"]))
			self.model.set_value(iter, COL_COMMENT, backup["comment"])
		self.button_back.set_sensitive(False)
		self.button_back.hide()
		self.button_forward.hide()
		self.button_apply.hide()
	
	def reload_nav_btns(self, button_back, button_forward, button_apply, user_data=False):
		module_logger.debug(_("Reloading navigation buttons for data backup."))
		# nav buttons
		self.button_back = button_back
		self.button_forward = button_forward
		self.button_apply = button_apply
		
		if user_data:
			self.button_back.connect("clicked", self.back_callback)
			self.button_forward.connect("clicked", self.forward_callback)
			self.button_apply.connect("clicked", self.forward_callback)
	
	def on_backup_selected(self, selection):
		model, iter = selection.get_selected()
		if iter is not None:
			self.selected_databackup = model.get_value(iter, COL_UUID)
			self.edit_button.set_sensitive(True)
			self.browse_button.set_sensitive(True)
			self.remove_button.set_sensitive(True)
	
	# Action definitions for buttons on the main panel at the top
	def on_backup_data(self, widget):
		module_logger.info(_("Starting Data backup..."))
		self.stack.set_visible_child_name("databackup_page1")
		self.button_back.set_sensitive(True)
		self.button_back.show()
		self.button_forward.show()
	
	def on_restore_data(self, widget):
		module_logger.info(_("Starting Data restore..."))
		# self.button_back.set_sensitive(True)
		# self.button_back.show()
		# self.button_forward.show()
		show_message(self.window, _("This feature has not been implented yet. Please wait for future releases."))
	
	def on_edit_databackup(self, widget):
		# On edit button press
		module_logger.debug(_("Editing backup file from database list."))
		show_message(self.window, _("This feature has not been implented yet. Please wait for future releases."))
	
	def on_browse_databackup(self, widget):
		# On browse button press
		module_logger.debug(_("Opening backup file/directory from database list."))
		# Open backup destination directory
		for i in range(len(self.data_db_list)):
			if self.data_db_list[i]['uuid'] == self.selected_databackup:
				backup_dict = self.data_db_list[i]
				if backup_dict["method"] == "rsync":
					subprocess.Popen(['xdg-open', backup_dict["destination"]])
				else:
					subprocess.Popen(['xdg-open', backup_dict["destination"]])
	
	def on_remove_databackup(self, widget):
		# On remove button press
		module_logger.debug(_("Removing data backup from database list."))
		# remove data backup
		for i in range(len(self.data_db_list)):
			if self.data_db_list[i]['uuid'] == self.selected_databackup:
				backup_dict = self.data_db_list[i]
				method = backup_dict["method"]
				if method == "rsync":
					pass
				else:
					backup_filepaths = glob.glob(os.path.join(backup_dict["destination"], backup_dict["filename"]+"*"))
				
				msg = "%s data backup" % method
				msg_detail = backup_dict["name"]
				if delete_confirm(self.window, msg, msg_detail):
					# Remove backup file(s)
					for filepath in backup_filepaths:
						try:
							module_logger.info(_("Deleteing file: %s" % filepath))
							os.remove(filepath)
						except OSError as e:
							# Log the error but continue to remove the entry from the DB list
							module_logger.error(_(f"Error removing file {filepath}: {e.strerror}"))
					if os.path.isdir(os.path.dirname(backup_dict["logfile"])):
						shutil.rmtree(os.path.dirname(backup_dict["logfile"]))
					# remove backup entry from database
					del self.data_db_list[i]
					module_logger.info(_(f"{msg} '{msg_detail}' removed from database list."))
					break
		
		self.db_manager.write_db(self.data_db_list)
		self.load_mainpage()
