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


# third-party library
import gettext
import gi
import locale

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

# imports from current package
from LeaptimeManager.common import APP, description, LOCALE_DIR, __version__


# i18n
locale.bindtextdomain(APP, LOCALE_DIR)
gettext.bindtextdomain(APP, LOCALE_DIR)
gettext.textdomain(APP)
_ = gettext.gettext


class AboutWindow():
	"""GUI class for About Window.
	
	This class displays the About window in where the user can see the information about Leaptime Manager project.
	"""
	
	def __init__(self, widget):
		authors = ['Himadri Sekhar Basu <https://hsbasu.github.io>']
		copyrights = "Copyright \xa9 2021-2022 Himadri Sekhar Basu"
		documenters = ['Himadri Sekhar Basu <https://hsbasu.github.io>']
		mainatainers = ['Himadri Sekhar Basu <https://hsbasu.github.io>']
		
		# initiaing about dialog and params
		self.about_dlg = Gtk.AboutDialog()
		self.about_dlg.set_transient_for(widget)

		self.about_dlg.set_icon_name("leaptime-manager")
		self.about_dlg.set_title(_("About"))

		self.about_dlg.set_logo_icon_name("leaptime-manager")
		self.about_dlg.set_program_name(_("Leaptime Manager"))
		self.about_dlg.set_version(__version__)

		self.about_dlg.set_website_label("Official Website")
		self.about_dlg.set_website("https://hsbasu.github.io/leaptime-manager")
		self.about_dlg.set_comments(description)
		self.about_dlg.set_copyright(copyrights)

		self.about_dlg.set_authors(authors)
		self.about_dlg.set_documenters(documenters)
		self.about_dlg.add_credit_section(_('Maintainer'), mainatainers)
        
		try:
			h = open('/usr/share/common-licenses/GPL', encoding="utf-8")
			s = h.readlines()
			gpl = ""
			for line in s:
				gpl += line
			h.close()
			self.about_dlg.set_license(gpl)
		except Exception as e:
			print(e)
        
		self.about_dlg.connect('response', self.__close)
	
	def show(self):
		# show the about dialog.
		self.about_dlg.show()
	
	def __close(self, w, res):
		"""Called when the user wants to close the about dialog.
		
		@param: action
			the window to close
		"""
		if res == Gtk.ResponseType.CANCEL or res == Gtk.ResponseType.DELETE_EVENT:
			w.destroy()
