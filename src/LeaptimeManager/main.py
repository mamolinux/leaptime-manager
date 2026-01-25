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
import locale
import logging
import setproctitle
import sys

# imports from current package
from LeaptimeManager.common import LOGFILE, __version__
from LeaptimeManager.cli_args import APP, LOCALE_DIR, command_line_args
from LeaptimeManager.gui import run_LTMwindow


# i18n
locale.bindtextdomain(APP, LOCALE_DIR)
gettext.bindtextdomain(APP, LOCALE_DIR)
gettext.textdomain(APP)
_ = gettext.gettext

setproctitle.setproctitle(APP)

# Parse arguments
parser = command_line_args()
args = parser.parse_args()

if args.show_version:
    print("%s: version %s" % (APP, __version__))
    sys.exit(0)

# Create logger
logger = logging.getLogger('LeaptimeManager')
# Set logging level
logger.setLevel(logging.DEBUG)
# create log formatter
log_format = logging.Formatter('%(asctime)s %(name)s:%(lineno)d - %(levelname)s: %(message)s')

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

def start_LTMCli():
	module_logger.info(_("Command line options are not available yet. Work In Progress..."))
	parser.print_help()
	sys.exit(0)

if args.start_window:
	# start GUI from terminal
	module_logger.debug(_("Starting GUI from terminal..."))
	# initiaing app window
	run_LTMwindow()
	sys.exit(0)
else:
	# initiaing cli
	start_LTMCli()
