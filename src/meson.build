pysrcinstalldir = python.get_install_dir() # python.get_path('platlib')
message(f'Python dir: @pysrcinstalldir@')

conf = configuration_data()
conf.set('PYTHON', python.full_path())
conf.set('pkgdatadir', pysrcinstalldir)

configure_file(
  input: 'leaptime-manager.in',
  output: 'leaptime-manager',
  configuration: conf,
  install: true,
  install_dir: bindir,
  install_mode: 'rwxr-xr-x'
)

subdir('LeaptimeManager')
