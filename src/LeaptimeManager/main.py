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
import logging
import setproctitle
import sys

from LeaptimeManager.common import APP, description, LOCALE_DIR, LOGFILE, __version__
from LeaptimeManager.gui import run_LTMwindow


# i18n
locale.bindtextdomain(APP, LOCALE_DIR)
gettext.bindtextdomain(APP, LOCALE_DIR)
gettext.textdomain(APP)
_ = gettext.gettext

setproctitle.setproctitle(APP)

# Parse arguments
parser = argparse.ArgumentParser(prog=APP, description=description, conflict_handler='resolve')

parser.add_argument('-g', '--gui', action='store_true', dest='start_window', default=False, help=("Start GUI window"))
parser.add_argument('-v', '--verbose', action='store_true', dest='show_debug', default=False, help=("Print debug messages to stdout i.e. terminal"))
parser.add_argument('-V', '--version', action='store_true', dest='show_version', default=False, help=("Show version and exit"))

args = parser.parse_args()

if args.show_version:
    print("%s: version %s" % (APP, __version__))
    sys.exit(0)

# Create logger
logger = logging.getLogger('LeaptimeManager')
# Set logging level
logger.setLevel(logging.DEBUG)
# create log formatter
log_format = logging.Formatter('%(asctime)s %(name)s - %(levelname)s: %(message)s')

# create file handler which logs only info messages
fHandler = logging.FileHandler(LOGFILE)
# Set level for FileHandler
fHandler.setLevel(logging.INFO)

# add formatter to the fHandler
fHandler.setFormatter(log_format)

# add the handler to the logger
logger.addHandler(fHandler)

if args.show_debug:
	# be verbose only when "-v[erbose]" is supplied
	# Create StreamHandler which logs even debug messages
	cHandler = logging.StreamHandler()
	# Set level for StreamHandler
	cHandler.setLevel(logging.DEBUG)
	
	# add formatter to the handler
	cHandler.setFormatter(log_format)

	# add the handler to the logger
	logger.addHandler(cHandler)

# module logger
module_logger = logging.getLogger('LeaptimeManager.main')

def start_LTMGui():
	# initiaing app window
	run_LTMwindow()
	sys.exit(0)

def start_LTMCli():
	module_logger.info("Work In Progress...")

if args.start_window:
	# start GUI from terminal
	module_logger.debug("Starting GUI from terminal...")
	start_LTMGui()

if __name__ == "__main__":
	if args.start_window:
		# start GUI from terminal
		start_LTMGui()
	else:
		start_LTMCli()
