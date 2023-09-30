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

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gio, Gdk

# imports from current package
from LeaptimeManager.common import APP, LOCALE_DIR, UI_PATH, __version__
from LeaptimeManager.about_window import AboutWindow
from LeaptimeManager.logger import LoggerWindow
from LeaptimeManager.appBackup import AppBackup
from LeaptimeManager.dataBackup import UserData

# logger
module_logger = logging.getLogger('LeaptimeManager.gui')

# i18n
locale.bindtextdomain(APP, LOCALE_DIR)
gettext.bindtextdomain(APP, LOCALE_DIR)
gettext.textdomain(APP)
_ = gettext.gettext


class leaptime_manager(Gtk.Application):
	# Main initialization routine
	def __init__(self, application_id, flags):
		Gtk.Application.__init__(self, application_id=application_id, flags=flags)
		self.connect("activate", self.activate)
	
	def activate(self, application):
		windows = self.get_windows()
		if (len(windows) > 0):
			window = windows[0]
			window.present()
			window.show()
		else:
			window = LeaptimeManagerWindow(self)
			self.add_window(window.window)
			window.window.show()

class LeaptimeManagerWindow():
	
	def __init__(self, application):
		
		self.application = application
		self.settings = Gio.Settings(schema_id="org.mamolinux.leaptime-manager")
		self.icon_theme = Gtk.IconTheme.get_default()
		self.user_data = True
		self.app_backup = False
		
		# Set the Glade files
		MainWindow = UI_PATH+"MainWindow.ui"
		app_backup_stack = UI_PATH+"app_backup.ui"
		user_data_stack = UI_PATH+"user_data.ui"
		self.builder = Gtk.Builder()
		self.builder.add_from_file(MainWindow)
		self.builder.add_from_file(app_backup_stack)
		self.builder.add_from_file(user_data_stack)
		
		# Create variables to quickly access dynamic widgets
		self.window = self.builder.get_object("main_window")
		self.main_box = self.builder.get_object("main_box")
		
		# Get app backup stack
		self.appbackup_stack = self.builder.get_object("app_backup_stack")
		self.main_box.add(self.appbackup_stack)
		self.appbackup_stack.set_visible(False)
		self.appbackup_stack.set_sensitive(False)
		
		# User data stack
		self.userdata_stack = self.builder.get_object("userdata_stack")
		self.main_box.add(self.userdata_stack)
		self.userdata_stack.set_visible(True)
		self.userdata_stack.set_sensitive(True)
		
		# Buttons
		self.apt_package_button = self.builder.get_object("apt_package")
		self.user_data_button = self.builder.get_object("user_data")
		
		self.new_button = self.builder.get_object("add_button")
		self.restore_button = self.builder.get_object("restore_button")
		self.edit_button = self.builder.get_object("edit_button")
		self.browse_button = self.builder.get_object("browse_button")
		self.remove_button = self.builder.get_object("remove_button")
		self.edit_button.set_sensitive(False)
		self.browse_button.set_sensitive(False)
		self.remove_button.set_sensitive(False)
		
		# nav buttons
		self.button_back = self.builder.get_object("button_back")
		self.button_forward = self.builder.get_object("button_forward")
		self.button_apply = self.builder.get_object("button_apply")
		
		self.apt_package_button.connect("clicked", self.show_appbackup_stack)
		self.user_data_button.connect("clicked", self.show_UserData_stack)
		
		self.new_button.connect("clicked", self.on_add_button)
		self.restore_button.connect("clicked", self.on_restore_button)
		self.edit_button.connect("clicked", self.on_edit_button)
		self.browse_button.connect("clicked", self.on_browse_button)
		self.remove_button.connect("clicked", self.on_remove_button)
		
		# Menubar
		accel_group = Gtk.AccelGroup()
		self.window.add_accel_group(accel_group)
		menu = self.builder.get_object("main_menu")
		# Add "Show Logs" option in drop-down menu
		item = Gtk.ImageMenuItem()
		item.set_image(Gtk.Image.new_from_icon_name("text-x-log", Gtk.IconSize.MENU))
		item.set_label(_("Show Logs"))
		item.connect("activate", self.show_logs, self.window)
		key, mod = Gtk.accelerator_parse("<Control>L")
		item.add_accelerator("activate", accel_group, key, mod, Gtk.AccelFlags.VISIBLE)
		menu.append(item)
		# Add "About" option in drop-down menu
		item = Gtk.ImageMenuItem()
		item.set_image(Gtk.Image.new_from_icon_name("help-about-symbolic", Gtk.IconSize.MENU))
		item.set_label(_("About"))
		item.connect("activate", self.open_about, self.window)
		key, mod = Gtk.accelerator_parse("F1")
		item.add_accelerator("activate", accel_group, key, mod, Gtk.AccelFlags.VISIBLE)
		menu.append(item)
		# Add "Quit" option in drop-down menu
		item = Gtk.ImageMenuItem(label=_("Quit"))
		image = Gtk.Image.new_from_icon_name("application-exit-symbolic", Gtk.IconSize.MENU)
		item.set_image(image)
		item.connect('activate', self.on_quit)
		key, mod = Gtk.accelerator_parse("<Control>Q")
		item.add_accelerator("activate", accel_group, key, mod, Gtk.AccelFlags.VISIBLE)
		key, mod = Gtk.accelerator_parse("<Control>W")
		item.add_accelerator("activate", accel_group, key, mod, Gtk.AccelFlags.VISIBLE)
		menu.append(item)
		# Show all drop-down menu options
		menu.show_all()
		
		self.UserData = UserData(self.builder, self.window, self.userdata_stack,
			    self.button_back, self.button_forward, self.button_apply, self.user_data)
		self.show_UserData_stack(self.window)
	
	def open_about(self, signal, widget):
		about_window = AboutWindow(widget)
		about_window.show()
	
	def show_logs(self, signal, widget):
		loggerwindow = LoggerWindow(widget)
		loggerwindow.show()
	
	def on_quit(self, widget):
		self.application.quit()
	
	def show_appbackup_stack(self, widget):
		module_logger.debug(_("Showing app backup stack."))
		
		# hide all other modules except app backup
		self.userdata_stack.set_visible(False)
		self.userdata_stack.set_sensitive(False)
		self.user_data = False
		self.appbackup_stack.set_visible(True)
		self.appbackup_stack.set_sensitive(True)
		self.app_backup = True
		
		self.AppBackup = AppBackup(self.builder, self.window, self.appbackup_stack,
			    self.button_back, self.button_forward, self.button_apply, self.app_backup)
		self.AppBackup.load_mainpage()
	
	def show_UserData_stack(self, widget):
		module_logger.debug(_("Showing data backup stack."))
		
		# hide all other modules except user data
		self.appbackup_stack.set_visible(False)
		self.appbackup_stack.set_sensitive(False)
		self.app_backup = False
		self.userdata_stack.set_visible(True)
		self.userdata_stack.set_sensitive(True)
		self.user_data = True
		
		self.UserData = UserData(self.builder, self.window, self.userdata_stack,
			    self.button_back, self.button_forward, self.button_apply, self.user_data)
		self.UserData.load_mainpage()
	
	def on_add_button(self, widget):
		module_logger.debug(_("Add button clicked."))
		if self.user_data:
			module_logger.debug(_("Starting new data backup process..."))
			self.UserData.on_backup_data(widget)
		if self.app_backup:
			module_logger.debug(_("Starting app backup process..."))
			self.AppBackup.on_backup_apps(widget)
	
	def on_restore_button(self, widget):
		if self.user_data:
			module_logger.debug(_("Starting data restore process..."))
			self.UserData.on_restore_data(widget)
		elif self.app_backup:
			module_logger.debug(_("Starting app restore process..."))
			self.AppBackup.on_restore_apps(widget)
	
	def on_edit_button(self, widget):
		if self.user_data:
			pass
		elif self.app_backup:
			module_logger.debug(_("Starting app backup editing process..."))
			self.AppBackup.on_edit_appbackup(widget)
	
	def on_browse_button(self, widget):
		if self.user_data:
			pass
		elif self.app_backup:
			module_logger.debug(_("Starting app backup browsing process..."))
			self.AppBackup.on_browse_appbackup(widget)
	
	def on_remove_button(self, widget):
		if self.user_data:
			pass
		elif self.app_backup:
			module_logger.debug(_("Starting app backup remove process..."))
			self.AppBackup.on_remove_appbackup(widget)

def run_LTMwindow():
	application = leaptime_manager("org.mamolinux.leaptime-manager", Gio.ApplicationFlags.FLAGS_NONE)
	application.run()
