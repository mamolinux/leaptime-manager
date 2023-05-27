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
import argparse
import gettext
import locale
import sys

from LeaptimeManager.common import APP, description, LOCALE_DIR, __version__
from LeaptimeManager.gui import run_LTMwindow


# i18n
locale.bindtextdomain(APP, LOCALE_DIR)
gettext.bindtextdomain(APP, LOCALE_DIR)
gettext.textdomain(APP)
_ = gettext.gettext


# Parse arguments
parser = argparse.ArgumentParser(prog=APP, description=description, conflict_handler='resolve')

parser.add_argument('-g', '--gui', action='store_true', dest='start_window', default=False, help=("Start GUI window"))
parser.add_argument('-V', '--version', action='store_true', dest='show_version', default=False, help=("Show version and exit"))

args = parser.parse_args()

if args.show_version:
    print("%s: version %s" % (APP, __version__))
    sys.exit(0)

def start_LTMGui():
	# initiaing app window
	run_LTMwindow()
	sys.exit(0)

def start_LTMCli():
	print("")

if args.start_window:
	# start GUI from terminal
	start_LTMGui()

if __name__ == "__main__":
	if args.start_window:
		# start GUI from terminal
		start_LTMGui()
	else:
		start_LTMCli()
