#!/usr/bin/env python3
# A shameless rip-off from MintBackup tool

# import the necessary modules!
import apt
# from apt import package
import apt_pkg
import gettext
import locale
import os
import shutil
import subprocess
import sys
import time

# from gi.repository import GLib

# i18n
APP = 'leaptime-manager'
LOCALE_DIR = "/usr/share/locale"
locale.bindtextdomain(APP, LOCALE_DIR)
gettext.bindtextdomain(APP, LOCALE_DIR)
gettext.textdomain(APP)
_ = gettext.gettext

# BACKUP_DIR = os.path.join(GLib.get_user_special_dir(GLib.UserDirectory.DIRECTORY_DOCUMENTS), _("MovebackTime"))
BACKUP_DIR = os.path.join("/media/backup/"+_("MovebackTime/apps"))

class AppBackup():
	
	def __init__(self) -> None:
		self.create_dirs()
		self.backup_pkg_save_to_file()
	
	def create_dirs(self):
		
		# for dirpath, dirnames, filenames in os.walk(BACKUP_DIR):
		# 	print(dirpath)
		# 	shutil.chown(dirpath, user_uid, user_gid)
		
		# print(user_uid, user_gid)
		if not os.path.exists(BACKUP_DIR):
			print("Creating backup directory in %s" % BACKUP_DIR)
			os.makedirs(BACKUP_DIR)
		# 	if os.geteuid() == 0:
		# 		print("We're root!")
		# 		os.makedirs(BACKUP_DIR)
		# 		os.chown(BACKUP_DIR, user_uid, user_gid)
		# 	else:
		# 		print("We're not root.")
		# 		subprocess.call(['sudo', 'python3', *sys.argv])
		# 		sys.exit()
		# else:
		# 	print("Backup directory exists in %s" % BACKUP_DIR)
		# 	if os.geteuid() == 0:
		# 		print("Making backup directory accessible")
		# 		os.chown(BACKUP_DIR, user_uid, user_gid)
		# 	else:
		# 		print("Backup directory not accessible")
		# 		subprocess.call(['sudo', 'python3', *sys.argv])
		# 		sys.exit()
		
	def backup_pkg(self):
		apt_pkg.init()
		
		cache = apt_pkg.Cache()					# all cache packages
		# package object list of all available packages in all repo
		allpacks_list = [pack for pack in cache.packages]	
		
		installer_log = "/var/log/installer/initial-status.gz"
		if not os.path.isfile(installer_log):
			return None
		import gzip
		try:
			installer_log = gzip.open(installer_log, "r").read().decode('utf-8').splitlines()
		except Exception as e:
			# There are a number of different exceptions here, but there's only one response
			print("Could not get initial installed packages list (check /var/log/installer/initial-status.gz): %s" % str(e))
			return None
		initial_status = [x[9:] for x in installer_log if x.startswith("Package: ")]
		if not initial_status:
			return None
			
		installed_pkgs = []
		auto_installed_pkgs = []
		for pack in allpacks_list:
			# list all installed packages
			if apt.Package(any, pack).is_installed:
				installed_pkgs.append(pack.name)
				# print(pack.name, "is installed.")
			else:
				pass
			# list all auto-installed packages
			if apt_pkg.DepCache(cache).is_auto_installed(pack):
				auto_installed_pkgs.append(pack.name)
				# print(pack.name, "is auto installed.")
			else:
				pass
		
		# sort installed packages and auto-installed packages
		installed_pkgs.sort()
		auto_installed_pkgs.sort()
		# find packages marked as manual
		marked_manual_pakgs = []
		for pack in installed_pkgs:
			if pack not in auto_installed_pkgs:
				marked_manual_pakgs.append(pack)
		
		# Manually installed packages
		installed_packages = []
		for pack in installed_pkgs:
			if pack not in initial_status:
				if pack in marked_manual_pakgs:
					installed_packages += [pack]
				
		return installed_packages
		
	def backup_pkg_save_to_file(self):

		installed_packages=self.backup_pkg()
		# Save the package selection
		filename = time.strftime("%Y-%m-%d-%H%M-packages.list", time.localtime())
		file_path = os.path.join(BACKUP_DIR, filename)		
		with open(file_path, "w") as f:
			for pack in installed_packages:
				f.write("%s\t%s\n" % (pack, "install"))

if __name__ == "__main__":
	AppBackup()
	