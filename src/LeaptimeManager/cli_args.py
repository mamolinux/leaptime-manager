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
import argparse
import gettext
import locale

from LeaptimeManager.common import  APP, LOCALE_DIR, description


# i18n
locale.bindtextdomain(APP, LOCALE_DIR)
gettext.bindtextdomain(APP, LOCALE_DIR)
gettext.textdomain(APP)
_ = gettext.gettext

def command_line_args():
	# Parse arguments
	parser = argparse.ArgumentParser(prog=APP, description=description, conflict_handler='resolve')
	
	parser.add_argument('-g', '--gui', action='store_true', dest='start_window', default=False, help=("Start GUI window"))
	parser.add_argument('-v', '--verbose', action='store_true', dest='show_debug', default=False, help=("Print debug messages to stdout i.e. terminal"))
	parser.add_argument('-V', '--version', action='store_true', dest='show_version', default=False, help=("Show version and exit"))
	
	return parser
