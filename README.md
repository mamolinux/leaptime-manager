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
	<a href="https://github.com/mamolinux/leaptime-manager/releases/download/1.0.4/leaptime-manager_1.0.4_all.deb">
		<img src="https://img.shields.io/github/downloads/mamolinux/leaptime-manager/1.0.4/leaptime-manager_1.0.4_all.deb?color=blue&label=Downloads%40Latest%20Binary" alt="GitHub release (latest by date and asset)">
	</a>
</p>

Aiming to be an all-in-one, friendly to new-users, GUI based backup manager for Debian/Ubuntu based systems. The main purpose of this application is to help user backup and restore every component on a Debian/Ubuntu based system ergonomically, elegantly and separately.

## Contents
- [ToDo List](#todo-list)
- [Download Latest Version](#download-latest-version)
	- [Stores/Ubuntu Private Archive](#storesubuntu-private-archive)
	- [Github Releases](#github-releases)
- [Features and Screenshots](#features-and-screenshots)
- [Dependencies](#dependencies)
	- [Build Dependencies](#build-dependencies)
	- [Runtime Dependencies](#runtime-dependencies)
	- [Debian/Ubuntu based systems](#debianubuntu-based-distro)
	- [Other Linux-based systems](#other-linux-based-distro)
- [Installation](#installation)
	- [1. Download and install binary files](#1-download-and-install-binary-files)
	- [2. Build and Install from source](#2-build-and-install-from-source)
		- [Debian/Ubuntu based systems](#debianubuntu-based-systems)
		- [Other Linux-based systems](#other-linux-based-systems)
- [User Manual](#user-manual)
- [Issue Tracking and Contributing](#issue-tracking-and-contributing)
	- [For Developers](#for-developers)
	- [Translation](#translation)
- [Contributors](#contributors)
	- [Authors](#author)

## ToDo List
**Software:**
1. [x] Apt backup
	1. [x] Scheduled app backup
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

### Stores/Ubuntu Private Archive
Add the Launchpad PPA
```$
sudo add-apt-repository ppa:mamolinux/gui-apps
sudo apt update
sudo apt install leaptime-manager
```

### Github Releases
Get the debian package archive from GitHub. For installation, check [here](#installation).
<p align="center">
	<a href="https://github.com/mamolinux/leaptime-manager/zipball/master">Download Source (.zip)</a></br>
	<a href="https://github.com/mamolinux/leaptime-manager/tarball/master">Download Source (.tar.gz)</a></br>
	<a href="https://github.com/mamolinux/leaptime-manager/releases/download/1.0.4/leaptime-manager_1.0.4_all.deb">Download Binary (.deb)</a>
</p>

## Features and Screenshots
1. Backup manually installed Apt packages to a list
2. Restore apt packages from backup lists
3. Backup user data to a tarball.

<p align="center">
	<img src="https://github.com/hsbasu/leaptime-manager/raw/gh-pages/screenshots/main-window-light.png" alt="Main Window (Light)">
	<img src="https://github.com/hsbasu/leaptime-manager/raw/gh-pages/screenshots/main-window-dark.png" alt="Main Window (Dark)">
	<img src="https://github.com/hsbasu/leaptime-manager/raw/gh-pages/screenshots/apt-backup-main-light.png" alt="App backup main page (Light)">
	<img src="https://github.com/hsbasu/leaptime-manager/raw/gh-pages/screenshots/apt-backup-main-dark.png" alt="App backup main page (Dark)">
</p>


## Dependencies
### Build Dependencies
The following dependencies are required to build **LeapTime Manager**.
```$
gettext
desktop-file-utils
libglib2.0-bin
gtk-update-icon-cache
meson
python3
python3-sphinx
python3-sphinx-argparse
```
### Runtime Dependencies
The following dependencies are required to run **LeapTime Manager**.
```
gir1.2-xapp-1.0
gir1.2-gtk-3.0
python3
python3-apt
python3-aptdaemon.gtk3widgets
python3-configobj
python3-gi
python3-setproctitle
python3-tldextract
```

### Debian/Ubuntu based distro
To install runtime dependencies on Debian/Ubuntu based systems, run:
```
sudo apt install gir1.2-xapp-1.0 gir1.2-gtk-3.0 python3 python3-aptdaemon.gtk3widgets \
python3-configobj python3-gi python3-setproctitle python3-tldextract
```
**Note**: If you are using `gdebi` to install **LeapTime Manager** from a downloaded/built `.deb` file, it will automatically install the dependencies and you can skip this step.

### Other Linux-based distro
Replace `apt install` in the command given in [Debian/Ubuntu based distros](#debianubuntu-based-distro) and use the command for the package manager of the target system(eg. `yum install`, `dnf install`, `pacman -S` etc.)

**Note**: There might be cases where one or more dependencies might not be available for your system. But that is highly unlikely. In such situations, please [create an issue](#issue-tracking-and-contributing).

## Installation
There are two ways, this app can be installed on a Debian/Ubuntu based system.

### 1. Download and install binary files
Download the latest binary .deb files from [here](https://github.com/mamolinux/leaptime-manager/releases/latest). Then install the GUI Frontend from terminal as
```$
sudo dpkg -i leaptime-manager*.deb
sudo apt install -f
```

### 2. Build and Install From Source
If you are having trouble installing the pre-built binary, build them from the source.

#### Debian/Ubuntu based systems
There are two methods, this app can be installed/used on a Debian/Ubuntu based system. First, download and unzip the source package using:
```
wget https://github.com/mamolinux/leaptime-manager/archive/refs/heads/master.zip
unzip master.zip
cd leaptime-manager-master
```

1. **Option 1:** Manually copying necessary files. For that, follow the steps below:
	1. Install python package sources using `meson`:
		```bash
		rm -rf builddir
		meson setup -Dprefix=$HOME/.local builddir
		meson compile -C builddir --verbose
		meson install -C builddir
		```
		It will install all files under `/home/<yourusername>/.local`. To **remove** the locally (`/home/<yourusername>/.local`) installed files, run:
		```bash
		ninja uninstall -C builddir
		```
	2. To manually install for all users:
		```bash
		rm -rf builddir
		meson setup builddir
		meson compile -C builddir --verbose
		sudo meson install -C builddir
		```
		The last step requires **Administrative Privilege**. So, be careful before using this. To **remove** the installed files, run:
		```bash
		sudo ninja uninstall -C builddir
		```

2. **Option 2:** Build a debian package and install it. To build a debian package on your own:
	1. from the `leaptime-manager-master` run:
		```bash
		dpkg-buildpackage --no-sign
		```
		This will create a `leaptime-manager_*.deb` package at `../leaptime-manager-master`.
	
	2. Install the debian package using
		```bash
		sudo dpkg -i ../leaptime-manager_*.deb
		sudo apt install -f
		```
After it is installed, run `leaptime-manager` from terminal or use the `leaptime-manager.desktop`.

#### Other Linux-based systems
1. Install the [dependencies](#other-linux-based-distro).
2. From instructions for [Debian/Ubuntu based systems](#debianubuntu-based-systems), follow **Option 1**.

## User Manual
Coming Soon or create a PR.

## Issue Tracking and Contributing
If you are interested to contribute and enrich the code, you are most welcome. You can do it by:
1. If you find a bug, to open a new issue with details: [Click Here](https://github.com/mamolinux/leaptime-manager/issues)
2. If you know how to fix a bug or want to add new feature/documentation to the existing package, please create a [Pull Request](https://github.com/mamolinux/leaptime-manager/compare).

### For Developers
I am managing these apps all by myself during my free time. There are times when I can't contribute for months. So a little help is always welcome. If you want to test **LeapTime Manager**,
1. Get the source package and unzip it using:
	```bash
	wget https://github.com/mamolinux/leaptime-manager/archive/refs/heads/master.zip
	unzip master.zip
	cd leaptime-manager-master
	```
2. Make desired modifications.
3. Manually install using [option 2](#2-build-and-install-from-source).
4. Test it by running in debug mode from terminal:	
	```bash
	leaptime-manager --gui --verbose
	```

### Translation
All translations are done using using [Launchpad Translations](https://translations.launchpad.net/mamolinux). To help translate **LeapTime Manager** in your favourite language follow these steps:
1. Go to [translations page](https://translations.launchpad.net/mamolinux/trunk/+pots/leaptime-manager) on Launchpad.
2. Click on the language, you want to translate.
3. Translate strings.
4. Finally, click on **Save & Continue**.

## Contributors

### Author
[Himadri Sekhar Basu](https://github.com/hsbasu) is the author and current maintainer.

## Donations
I am a freelance programmer. So, If you like this app and would like to offer me a coffee ( &#9749; ) to motivate me further, you can do so via:

[![](https://liberapay.com/assets/widgets/donate.svg)](https://liberapay.com/hsbasu/donate)
[![](https://www.paypalobjects.com/webstatic/i/logo/rebrand/ppcom.svg)](https://paypal.me/hsbasu)
[![](https://hsbasu.github.io/styles/icons/logo/svg/upi-logo.svg)](https://hsbasu.github.io/images/upi-qr.jpg)
