# Copyright (C) 2023 Himadri Sekhar Basu <hsb10@iitbbs.ac.in>
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
import json
import locale
import logging

# imports from current package
from LeaptimeManager.common import APP, LOCALE_DIR, LTM_backend

# i18n
locale.bindtextdomain(APP, LOCALE_DIR)
gettext.bindtextdomain(APP, LOCALE_DIR)
gettext.textdomain(APP)
_ = gettext.gettext

# logger
module_logger = logging.getLogger('LeaptimeManager.database_rw')

class appbackup_db():
	
	def __init__(self):
		self.manager = LTM_backend()
	
	def write_db(self, app_db_list):
		module_logger.debug(_("Writing backup to database."))
		json_object = json.dumps(app_db_list, indent=2)
		with open(self.manager.app_backup_db, 'w') as f:
			f.write(json_object)
			f.write("\n")
	
	def read_db(self):
		module_logger.debug(_("Reading backups from database."))
		with open(self.manager.app_backup_db, 'r') as f:
			try:
				app_db_list = json.load(f)
			except:
				app_db_list = []
			return app_db_list

class databackup_db():
	
	def __init__(self):
		self.manager = LTM_backend()
	
	def write_db(self, data_db_list, name, method, src, dest, timestamp, repeat, comment):
		module_logger.debug(_("Writing data backup to database."))
		data_db_dict = {
			 "name" : name,
			 "method" : method,
			 "source" : src,
			 "destination" : dest,
			 "created" : timestamp,
			 "repeat" : repeat,
			 "comment" : comment
			}
		data_db_list.append(data_db_dict)
		json_object = json.dumps(data_db_list, indent=2)
		with open(self.manager.data_backup_db, 'w') as f:
			f.write(json_object)
			f.write("\n")
	
	def read_db(self):
		module_logger.debug(_("Reading data backups from database."))
		with open(self.manager.data_backup_db, 'r') as f:
			try:
				data_db_list = json.load(f)
			except:
				data_db_list = []
			return data_db_list
