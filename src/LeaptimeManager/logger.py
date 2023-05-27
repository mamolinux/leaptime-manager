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

# import the necessary modules!
import gettext
import gi
import locale

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

from LeaptimeManager.common import APP, LOCALE_DIR, LOGFILE, UI_PATH


# i18n
locale.bindtextdomain(APP, LOCALE_DIR)
gettext.bindtextdomain(APP, LOCALE_DIR)
gettext.textdomain(APP)
_ = gettext.gettext


class LoggerWindow():
	"""GUI class for Logger Window.
	
	This class displays the Logger window in where the user can see the logs of Leaptime Manager project.
	"""
	
	def __init__(self, widget):
		try:
			h = open(LOGFILE, encoding="utf-8")
			s = h.readlines()
			LTMlogs = ""
			for line in s:
				LTMlogs += line
			h.close()
		except Exception as e:
			LTMlogs = str(e)
		
		logger_ui = UI_PATH+"logger.ui"
		log_builder = Gtk.Builder()
		log_builder.add_from_file(logger_ui)
		self.logger_dlg = log_builder.get_object("logger_dlg")
		self.logger_dlg.set_transient_for(widget)
		self.logger_dlg.set_title(_("Leaptime Manager Logs"))
		self.logger_dlg.add_buttons(Gtk.STOCK_CLOSE, Gtk.ResponseType.CLOSE)
		logview = log_builder.get_object("log_view")
		logview.set_editable(False)
		logview.set_wrap_mode(Gtk.WrapMode.WORD)
		logview.get_buffer().set_text(LTMlogs)
		
		self.logger_dlg.connect("response", self.__close)
	
	def show(self):
		# show the about dialog.
		self.logger_dlg.show()
	
	def __close(self, w, res):
		"""Called when the user wants to close the about dialog.
		
		@param: action
			the window to close
		"""
		if res == Gtk.ResponseType.CLOSE or res == Gtk.ResponseType.DELETE_EVENT:
			w.destroy()
