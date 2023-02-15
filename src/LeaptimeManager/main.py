import argparse
import gettext
import locale
import sys

from LeaptimeManager.common import APP, LOCALE_DIR, __version__
from LeaptimeManager.gui import run_LTMwindow


# i18n
locale.bindtextdomain(APP, LOCALE_DIR)
gettext.bindtextdomain(APP, LOCALE_DIR)
gettext.textdomain(APP)
_ = gettext.gettext

description = _('Very simple Python3-based GUI application to generate secure and random password.')

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
