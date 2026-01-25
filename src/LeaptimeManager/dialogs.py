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
import gettext
import gi
import locale
import logging

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

# imports from current package
from LeaptimeManager.cli_args import  APP, LOCALE_DIR

# i18n
locale.bindtextdomain(APP, LOCALE_DIR)
gettext.bindtextdomain(APP, LOCALE_DIR)
gettext.textdomain(APP)
_ = gettext.gettext

# logger
module_logger = logging.getLogger('LeaptimeManager.dialogs')

def show_message(window, message, message_type=Gtk.MessageType.WARNING):
	dialog = Gtk.MessageDialog(window, Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT, message_type, Gtk.ButtonsType.OK, message)
	dialog.set_title(_("LeapTime Manager"))
	dialog.set_position(Gtk.WindowPosition.CENTER)
	dialog.run()
	dialog.destroy()

def delete_confirm(window, message_head, msg_detail, message_type=Gtk.MessageType.WARNING):
	dialog = Gtk.MessageDialog(window, message_type)
	dialog.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_DELETE, Gtk.ResponseType.YES)
	dialog.set_title(_("Remove %s" % message_head))
	dialog.set_property("text", _("Are you sure you want to delete '%s'?") % msg_detail)
	dialog.format_secondary_text(_("This backup will be permanently lost."))
	dialog.set_position(Gtk.WindowPosition.CENTER)
	if dialog.run() == Gtk.ResponseType.YES:
		dialog.destroy()
		return True
	else:
		dialog.destroy()
		return False
