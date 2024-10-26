python_sources = [
  'about_window.py',
	'appBackup.py',
	'cli_args.py',
	'common.py',
	'dataBackup.py',
	'database_rw.py',
	'dialogs.py',
	'gui.py',
	'__init__.py',
	'logger.py',
	'main.py',
]

version_file = configure_file(
  input: 'VERSION.in',
  output: 'VERSION',
  configuration: {
    'version': meson.project_version(),
  }
)

args_file = configure_file(
  input: 'cli_args.py',
  output: 'cli_args.py',
  configuration: {
    'appname': application_id,
    'localedir': join_paths(prefix, get_option('localedir')),
  }
)

python.install_sources(
  python_sources, version_file, args_file,
  subdir: 'LeaptimeManager',
  preserve_path: true,
)

# Install assets like ui and icons
ui = files('ui/app_backup.ui', 'ui/logger.ui', 'ui/MainWindow.ui', 'ui/user_data.ui')

install_data(
  ui,
  install_dir: join_paths(pysrcinstalldir, 'LeaptimeManager', 'ui')
)
