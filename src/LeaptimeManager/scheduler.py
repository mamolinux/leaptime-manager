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
import datetime
import gettext
import gi
import locale
import logging

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib


# imports from current package
from LeaptimeManager.cli_args import  APP, LOCALE_DIR

# i18n
locale.bindtextdomain(APP, LOCALE_DIR)
gettext.bindtextdomain(APP, LOCALE_DIR)
gettext.textdomain(APP)
_ = gettext.gettext

# logger
module_logger = logging.getLogger('LeaptimeManager.scheduler')

class ScheduleManager:
	"""Manages scheduling for backups with support for various intervals."""

	INTERVALS = {
		'hourly': 'Hourly',
		'daily': 'Daily',
		'weekly': 'Weekly',
		'monthly': 'Monthly',
		'custom': 'Custom Interval'
	}

	def __init__(self):
		self.schedules = {}

	@staticmethod
	def parse_interval(interval_str):
		"""Parse interval string like 'daily', 'hourly', 'weekly', 'monthly', or 'custom:N:hours/days'."""
		if not interval_str:
			return None

		parts = interval_str.split(':')
		interval_type = parts[0]

		if interval_type in ['hourly', 'daily', 'weekly', 'monthly']:
			return {'type': interval_type}
		elif interval_type == 'custom' and len(parts) == 3:
			return {
				'type': 'custom',
				'value': int(parts[1]),
				'unit': parts[2]  # 'hours', 'days', 'weeks'
			}
		return None

	@staticmethod
	def format_interval(interval_dict):
		"""Format interval dict to string for database storage."""
		if not interval_dict:
			return ""

		interval_type = interval_dict.get('type', '')
		if interval_type in ['hourly', 'daily', 'weekly', 'monthly']:
			return interval_type
		elif interval_type == 'custom':
			value = interval_dict.get('value', 1)
			unit = interval_dict.get('unit', 'days')
			return f"custom:{value}:{unit}"
		return ""

	@staticmethod
	def get_next_run_time(interval_dict, last_run=None):
		"""Calculate next run time based on interval and last run time."""
		import datetime

		if not interval_dict:
			return None

		if last_run is None:
			last_run = datetime.datetime.now()
		elif isinstance(last_run, str):
			try:
				last_run = datetime.datetime.strptime(last_run, "%Y-%m-%d %H:%M")
			except ValueError:
				last_run = datetime.datetime.now()

		interval_type = interval_dict.get('type', '')

		if interval_type == 'hourly':
			return last_run + datetime.timedelta(hours=1)
		elif interval_type == 'daily':
			return last_run + datetime.timedelta(days=1)
		elif interval_type == 'weekly':
			return last_run + datetime.timedelta(weeks=1)
		elif interval_type == 'monthly':
			# Approximate month as 30 days
			return last_run + datetime.timedelta(days=30)
		elif interval_type == 'custom':
			value = interval_dict.get('value', 1)
			unit = interval_dict.get('unit', 'days')

			if unit == 'hours':
				return last_run + datetime.timedelta(hours=value)
			elif unit == 'days':
				return last_run + datetime.timedelta(days=value)
			elif unit == 'weeks':
				return last_run + datetime.timedelta(weeks=value)

		return None

	@staticmethod
	def is_due(interval_str, last_run):
		"""Check if a backup is due based on interval and last run time."""
		interval_dict = ScheduleManager.parse_interval(interval_str)
		if not interval_dict:
			return False

		next_run = ScheduleManager.get_next_run_time(interval_dict, last_run)
		if next_run is None:
			return False

		return datetime.datetime.now() >= next_run

	@staticmethod
	def get_interval_description(interval_str):
		"""Get human-readable description of interval."""
		interval_dict = ScheduleManager.parse_interval(interval_str)
		if not interval_dict:
			return _("No schedule")

		interval_type = interval_dict.get('type', '')

		if interval_type == 'hourly':
			return _("Every hour")
		elif interval_type == 'daily':
			return _("Every day")
		elif interval_type == 'weekly':
			return _("Every week")
		elif interval_type == 'monthly':
			return _("Every month")
		elif interval_type == 'custom':
			value = interval_dict.get('value', 1)
			unit = interval_dict.get('unit', 'days')
			unit_trans = {
				'hours': _('hour(s)'),
				'days': _('day(s)'),
				'weeks': _('week(s)')
			}
			return _("Every %(value)d %(unit)s") % {'value': value, 'unit': unit_trans.get(unit, unit)}

		return _("Unknown schedule")

class TimeChooserButton(Gtk.Button):
	
	def __init__(self, follow_current=False, time=None):
		super(TimeChooserButton, self).__init__()
		# self.set_sensitive(True)
		self.set_visible(True)
		
		if not follow_current and time is not None:
			self.set_time(time)
		else:
			self.set_time(datetime.datetime.now())
		
		if follow_current:
			GLib.timeout_add_seconds(1, self.update_time)
		
		self.connect('clicked', self.on_button_clicked)
	
	def on_button_clicked(self, *args):
		dialog = TimeChooserDialog(self.time, self.get_toplevel())
		response = dialog.run()
		if response == Gtk.ResponseType.OK:
			self.set_time(dialog.get_time())
		dialog.destroy()
	
	def update_time(self, *args):
		self.set_time(datetime.datetime.now().time())
		return True
	
	def get_time(self):
		return self.time
	
	def set_time(self, time):
		"""Sets the time of the widget.
		Time can be a time or datetime class from the datetime module or a (h,m) or (h,m,s) tuple.
		"""
		if isinstance(time, datetime.time):
			self.time = time
		elif isinstance(time, datetime.datetime):
			self.time = time.time()
		elif isinstance(time, tuple):
			self.time = datetime.time(*time)
		else:
			raise ValueError('Invalid time format. Must be of type datetime.time, datetime.datetime, or a tuple of the form (hour, minute[, second])')
		
		self.update_label()
	
	def update_label(self):
		format_code = '%l:%M:%S %p'
		time_string = self.time.strftime(format_code)
		self.set_label(time_string)

class TimeChooserDialog(Gtk.Dialog):
	def __init__(self, time, window):
		super(TimeChooserDialog, self).__init__(title = _("Select a time"),
												transient_for = window,
												flags = Gtk.DialogFlags.MODAL,
												buttons = (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
														 Gtk.STOCK_OK, Gtk.ResponseType.OK))

		self.time = {'hour': time.hour, 'minute': time.minute, 'second': time.second}
		self.markup = lambda text: '<span weight="bold" size="xx-large">%s</span>' % text
		
		content = self.get_content_area()
		
		grid = Gtk.Grid(halign=Gtk.Align.CENTER)
		grid.set_column_spacing(10)
		content.pack_start(grid, False, False, 0)
		
		grid.attach(Gtk.Label(self.markup(_("Hour")), use_markup=True), 0, 0, 1, 1)
		grid.attach(Gtk.Label(self.markup(':'), use_markup=True), 1, 2, 1, 1)
		grid.attach(Gtk.Label(self.markup(_("Minute")), use_markup=True), 2, 0, 1, 1)
		grid.attach(Gtk.Label(self.markup(':'), use_markup=True), 3, 2, 1, 1)
		grid.attach(Gtk.Label(self.markup(_("Second")), use_markup=True), 4, 0, 1, 1)
		
		unit_defs = [('hour', 0), ('minute', 2), ('second', 4)]
		
		self.labels = {}
		for ttype, column in unit_defs:
			self.labels[ttype] = Gtk.Label(self.markup(self.time[ttype]), use_markup=True)
			grid.attach(self.labels[ttype], column, 2, 1, 1)
			
			up_button = Gtk.Button.new_from_icon_name('pan-up-symbolic', 6)
			down_button = Gtk.Button.new_from_icon_name('pan-down-symbolic', 6)
			up_button.set_relief(2)
			down_button.set_relief(2)
			grid.attach(up_button, column, 1, 1, 1)
			grid.attach(down_button, column, 3, 1, 1)
			up_button.connect('clicked', self.shift_time, ttype, 1)
			down_button.connect('clicked', self.shift_time, ttype, -1)
		
		content.show_all()
	
	def shift_time(self, button, ttype, offset):
		self.time[ttype] += offset
		self.time['hour'] = self.time['hour'] % 24
		self.time['minute'] = self.time['minute'] % 60
		self.time['second'] = self.time['second'] % 60
		self.labels[ttype].set_label(self.markup(self.time[ttype]))
	
	def get_time(self):
		return datetime.time(self.time['hour'], self.time['minute'], self.time['second'])
