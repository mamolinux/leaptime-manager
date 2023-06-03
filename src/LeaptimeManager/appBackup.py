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
# along with leaptime-manager. If not, see <http://www.gnu.org/licenses/>
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
from gi.repository import Gtk, GLib

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
	
	def __init__(self, builder, window, stack, button_back, button_forward, button_apply) -> None:
		module_logger.info("Initializing App backup module...")
		self.builder = builder
		self.window = window
		self.stack = stack
		
		# nav buttons
		self.button_back = button_back
		self.button_forward = button_forward
		self.button_apply = button_apply
		
		self.button_back.connect("clicked", self.back_callback)
		self.button_forward.connect("clicked", self.forward_callback)
		self.button_apply.connect("clicked", self.forward_callback)
		
		# packages list
		t = self.builder.get_object("treeview_packages")
		self.builder.get_object("button_select").connect("clicked", self.set_selection, t, True, False)
		self.builder.get_object("button_deselect").connect("clicked", self.set_selection, t, False, False)
		tog = Gtk.CellRendererToggle()
		tog.connect("toggled", self.toggled_cb, t)
		c1 = Gtk.TreeViewColumn("", tog, active=0)
		c1.set_cell_data_func(tog, self.celldatamethod_checkbox)
		t.append_column(c1)
		c2 = Gtk.TreeViewColumn("", Gtk.CellRendererText(), markup=2)
		t.append_column(c2)

		file_filter = Gtk.FileFilter()
		file_filter.add_pattern ("*.list")
		filechooser = self.builder.get_object("filechooserbutton_package_source")
		filechooser.connect("file-set", self.restore_pkg_validate_file)
		filechooser.set_filter(file_filter)
	
	def back_callback(self, widget):
		# Back button
		page = self.stack.get_visible_child_name()
		if page == "appbackup_page2":
			self.stack.set_visible_child_name("appbackup_page1")
			self.button_back.set_sensitive(False)
			self.button_back.hide()
			self.button_forward.hide()
		elif page == "appbackup_page3":
			self.stack.set_visible_child_name("appbackup_page2")
			self.show_apps_list()
			self.button_back.set_sensitive(True)
			self.button_back.show()
			self.button_forward.show()
	
	def forward_callback(self, widget):
		# Go forward
		page = self.stack.get_visible_child_name()
		self.builder.get_object("button_back").set_sensitive(True)
		if page == "appbackup_page2":
			# show progress of packages page
			self.stack.set_visible_child_name("appbackup_page3")
			self.button_forward.set_sensitive(True)
			self.button_back.show()
			self.button_forward.show()
		elif page == "appbackup_page3":
			self.backup_dest = self.builder.get_object("filechooserbutton_package_dest").get_filename()
			self.backup_pkg_save_to_file()
			self.stack.set_visible_child_name("appbackup_page1")
			self.button_back.hide()
			self.button_forward.hide()
	
	def toggled_cb(self, ren, path, treeview):
		model = treeview.get_model()
		iter = model.get_iter(path)
		if iter != None:
			checked = model.get_value(iter, 0)
			model.set_value(iter, 0, (not checked))
	
	def celldatamethod_checkbox(self, column, cell, model, iter, user_data):
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
	
	def backup_pkg_list(self):
		apt_pkg.init()
		
		self.cache = apt_pkg.Cache()					# all cache packages
		# package object list of all available packages in all repo
		allpacks_list = [pack for pack in self.cache.packages]
		
		installer_log = "/var/log/installer/initial-status.gz"
		if not os.path.isfile(installer_log):
			return None
		import gzip
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
	
	def backup_pkg_save_to_file(self):
		
		# Save the package selection
		filename = time.strftime("%Y-%m-%d-%H%M-packages.list", time.localtime())
		file_path = os.path.join(self.backup_dest, filename)
		with open(file_path, "w") as f:
			for pack in self.installed_packages:
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
			self.show_message(Gtk.window(), _("An error occurred while reading the file."))
			module_logger.debug(detail)
	
	def show_apps_list(self):
		module_logger.debug(_("Showing backup apps list..."))
		model = Gtk.ListStore(bool, str, str)
		model.set_sort_column_id(1, Gtk.SortType.ASCENDING)
		self.installed_packages = self.backup_pkg_list()
		
		package_records = apt_pkg.PackageRecords(self.cache)
		for item in self.installed_packages:
			try:
				name = item
				if name in self.cache:
					pkg = self.cache[name]
					if pkg.current_ver:
						package_records.lookup(pkg.version_list[0].translated_description.file_list[0])
						desc = "%s\n<small>%s</small>" % (pkg.name, GLib.markup_escape_text(package_records.short_desc))
						model.append([True, pkg.name, desc])
			except Exception as e:
				print(e)
		
		self.builder.get_object("treeview_packages").set_model(model)
	
	def backup_apps(self, widget):
		module_logger.debug(_("Starting app backup list process"))
		self.stack.set_visible_child_name("appbackup_page2")
		self.button_back.set_sensitive(True)
		self.button_back.show()
		self.button_forward.show()
		self.show_apps_list()
