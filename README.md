# [LeapTime Manager](https://hsbasu.github.io/leaptime-manager)

# Work In Progress
This App is currently under **development**. So, This is not what a regular user would expect. If you are a developer and would like to contribute, only then download or fork this repo.

<p align="center">
  	<img src="https://raw.githubusercontent.com/mamolinux/leaptime-manager/master/data/icons/leaptime-manager.svg?sanitize=true" height="128" alt="Logo">
</p>

<p align="center">
	<a href="https://github.com/mamolinux/leaptime-manager/actions/workflows/ci.yml">
		<img src="https://img.shields.io/github/actions/workflow/status/mamolinux/leaptime-manager/ci.yml?branch=master&label=CI%20Build" alt="CI build">
	</a>
	<a href="https://github.com/mamolinux/leaptime-manager/actions/workflows/codeql-analysis.yml">
		<img src="https://img.shields.io/github/actions/workflow/status/mamolinux/leaptime-manager/codeql-analysis.yml?branch=master&label=CodeQL%20Build" alt="CodeQL build">
	</a>
	<a href="https://github.com/mamolinux/leaptime-manager/blob/master/LICENSE">
		<img src="https://img.shields.io/github/license/mamolinux/leaptime-manager?label=License" alt="License">
	</a>
  	<a href="#">
		<img src="https://img.shields.io/github/repo-size/mamolinux/leaptime-manager?label=Repo%20size" alt="GitHub repo size">
  	</a>
	<a href="https://github.com/mamolinux/leaptime-manager/issues" target="_blank">
		<img src="https://img.shields.io/github/issues/mamolinux/leaptime-manager?label=Issues" alt="Open Issues">
	</a>
	<a href="https://github.com/mamolinux/leaptime-manager/pulls" target="_blank">
		<img src="https://img.shields.io/github/issues-pr/mamolinux/leaptime-manager?label=PR" alt="Open PRs">
	</a>
  	<a href="https://github.com/mamolinux/leaptime-manager/releases/latest">
    	<img src="https://img.shields.io/github/v/release/mamolinux/leaptime-manager?label=Latest%20Stable%20Release" alt="GitHub release (latest by date)">
  	</a>
	<a href="#download-latest-version">
		<img src="https://img.shields.io/github/downloads/mamolinux/leaptime-manager/total?label=Downloads" alt="Downloads">
	</a>
	<a href="https://github.com/mamolinux/leaptime-manager/releases/download/1.0.2/leaptime-manager_1.0.2_all.deb">
		<img src="https://img.shields.io/github/downloads/mamolinux/leaptime-manager/1.0.2/leaptime-manager_1.0.2_all.deb?color=blue&label=Downloads%40Latest%20Binary" alt="GitHub release (latest by date and asset)">
	</a>
</p>

Aiming to be an all-in-one, friendly to new-users, GUI based backup manager for Debian/Ubuntu based systems. The main purpose of this application is to help user backup and restore every component on a Debian/Ubuntu based system ergonomically, elegantly and separately.

## ToDo List
**Software:**
1. [x] Apt backup
2. [x] Apt restore

**Data:**
Data backup should have two modes:
1. [ ] Sync mode- where file(s) or directories are synchronized continuously with another keeping only the latest version. Useful for backing up static data like some script which are updated time to time or security keys like ssh or gpg keys. Use one of the following modes
    1. [ ] Compressed backup - tar ball of data (Reduces disk-space usage)
    2. [ ] Rsync: using `rsync`
    3. [ ] Add option for user-defined time interval to sync data

3. [ ] Incremental mode: Where incremental backups are created like any other backup app. Use one of the following modes
    1. [ ] Compressed backup - tar ball of data (Reduces disk-space usage)
    2. [ ] Rsync: using `rsync`
    1. [ ] Add option for user-defined time interval to backup data

## Download Latest Version
<p align="center">
	<a href="https://github.com/mamolinux/leaptime-manager/zipball/master">Download Source (.zip)</a></br>
	<a href="https://github.com/mamolinux/leaptime-manager/tarball/master">Download Source (.tar.gz)</a></br>
	<a href="https://github.com/mamolinux/leaptime-manager/releases/download/1.0.2/leaptime-manager_1.0.2_all.deb">Download Binary (.deb)</a>
</p>

## Features and Screenshots
1. Backup manually installed applications to a list
2. Restore applications from backup lists

<p align="center">
	<img src="https://github.com/hsbasu/leaptime-manager/raw/gh-pages/screenshots/main-window-light.png" alt="Main Window (Light)">
	<img src="https://github.com/hsbasu/leaptime-manager/raw/gh-pages/screenshots/main-window-dark.png" alt="Main Window (Dark)">
	<img src="https://github.com/hsbasu/leaptime-manager/raw/gh-pages/screenshots/apt-backup-main-light.png" alt="App backup main page (Light)">
	<img src="https://github.com/hsbasu/leaptime-manager/raw/gh-pages/screenshots/apt-backup-main-dark.png" alt="App backup main page (Dark)">
</p>


## Contents
- [ToDo List](#todo-list)
- [Download Latest Version](#download-latest-version)
- [Features and Screenshots](#features-and-screenshots)
- [Dependencies](#dependencies)
	- [Debian/Ubuntu based systems](#debianubuntu-based-distro)
	- [Other Linux-based systems](#other-linux-based-distro)
- [Installation](#build-and-install-the-latest-version)
	- [Debian/Ubuntu based systems](#debianubuntu-based-systems)
	- [Other Linux-based systems](#other-linux-based-systems)
	- [For Developers](#for-developers)
- [User Manual](#user-manual)
- [Issue Tracking and Contributing](#issue-tracking-and-contributing)
- [Contributors](#contributors)
	- [Authors](#author)

## Dependencies
```
python3
python3-aptdaemon.gtk3widgets
python3-configobj
python3-gi
python3-setproctitle
python3-tldextract
```
To use or test LeapTime Manager, you need these dependencies to be installed.

### Debian/Ubuntu based distro
To install dependencies on Debian/Ubuntu based systems, run:
```
sudo apt install python3 python3-aptdaemon.gtk3widgets python3-configobj \
python3-gi python3-setproctitle python3-tldextract
```
**Note**: If you are using `gdebi` to install **LeapTime Manager** from a `.deb` file, it will automatically install the dependencies and you can skip this step.

### Other Linux-based distro
Replace `apt install` in the command given in [Debian/Ubuntu based distros](#debianubuntu-based-distro) and use the command for the package manager of the target system(eg. `yum install`, `dnf install`, `pacman -S` etc.)

**Note**: There might be cases where one or more dependencies might not be available for your system. But that is highly unlikely. In such situations, please [create an issue](#issue-tracking-and-contributing).

## Build and Install the Latest Version
### Debian/Ubuntu based systems
There are two methods, this app can be installed/used on a Debian/Ubuntu based system. First, download and unzip the source package using:
```
wget https://github.com/mamolinux/leaptime-manager/archive/refs/heads/master.zip
unzip master.zip
cd leaptime-manager-master
```

1. **Option 1:** Manually copying necessary files to root (`/`). For that, follow the steps below:
	1. [**Optional**] [**In Progress**] To make translations/locales in languages other than **English**, run:
		```
		make
		```
		from the `leaptime-manager-master` in a terminal. It will create the translations/locales in `usr/share/locale`.
	
	2. Install python package using `pip3`:
		```
		sudo pip3 install .
		```
		It will install all files under `/usr/local/`
	3. Compile `schemas` using:
		```
		sudo glib-compile-schemas /usr/local/share/glib-2.0/schemas
		```

2. **Option 2:** Build a debian package and install it. To build a debian package on your own:
	1. from the `leaptime-manager-master` run:
		```
		dpkg-buildpackage --no-sign
		```
		This will create a `leaptime-manager_*.deb` package at `../leaptime-manager-master`.
	
	2. Install the debian package using
		```
		sudo dpkg -i ../leaptime-manager_*.deb
		sudo apt install -f
		```
After it is installed, run `leaptime-manager` from terminal or use the `leaptime-manager.desktop`.

### Other Linux-based systems
1. Install the [dependencies](#other-linux-based-distro).
2. From instructions for [Debian/Ubuntu based systems](#debianubuntu-based-systems), follow **Option 1**.


### For Developers
Instructions for devs are coming soon or create a [PR](https://github.com/mamolinux/leaptime-manager/compare).

**I have no knowledge on how to use `meson` or `npm` for testing. If you can offer any help regarding this, please start a discussion [here](https://github.com/mamolinux/leaptime-manager/discussions) or create a [PR](https://github.com/mamolinux/leaptime-manager/compare). It will be more than welcome.**

## User Manual
Coming Soon or create a PR.

## Issue Tracking and Contributing
If you are interested to contribute and enrich the code, you are most welcome. You can do it by:
1. If you find a bug, to open a new issue with details: [Click Here](https://github.com/mamolinux/leaptime-manager/issues)

2. If you know how to fix a bug or want to add new feature/documentation to the existing package, please create a [Pull Request](https://github.com/mamolinux/leaptime-manager/compare).

## Contributors

### Author
[Himadri Sekhar Basu](https://github.com/hsbasu) is the author and current maintainer.

## Donations
I am a freelance programmer. So, If you like this app and would like to offer me a coffee ( &#9749; ) to motivate me further, you can do so via:

[![](https://liberapay.com/assets/widgets/donate.svg)](https://liberapay.com/hsbasu/donate)
[![](https://www.paypalobjects.com/webstatic/i/logo/rebrand/ppcom.svg)](https://paypal.me/hsbasu)
[![](https://hsbasu.github.io/styles/icons/logo/svg/upi-logo.svg)](https://hsbasu.github.io/images/upi-qr.jpg)
