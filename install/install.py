import os
import re
import sys
import subprocess
from argparse import ArgumentParser, RawTextHelpFormatter
from collections import OrderedDict

parser = ArgumentParser(formatter_class=RawTextHelpFormatter, prog='install.py',
description="""
%(prog)s installs python projects for dataeval from MKS based on install.cfg.""",
epilog="""
If dataeval sandboxes are not beside the install project, please use
--dataeval-root option to set up.

The program tries to find the location of MKS Integrity client, which can take
some time. That can be avoided, if client path is set with --si option, like
--si C:\KBApps\Integrity\IntegrityClient10\bin\si.exe

If you use --resync option, then %(prog)s will overwrite every changes except
dataevalaebs project and the others which are set with --no-overwrite option.
""")

parser.add_argument('--dataeval-root',
                    default=os.path.abspath(os.path.join(__file__, '..', '..')),
                    help='root directory of dateval projects [%(default)s]')
parser.add_argument('--resync', action='store_true', default=False,
                    help='omit sandbox creation, only resync and register the existing projects')
parser.add_argument('--register', action='store_true', default=False,
                    help='omit both sandbox creation and resync, only register the existing projects')
parser.add_argument('--si',
                    help='full name of mks integrity client')
parser.add_argument('--no-overwrite', action='append', default=['dataevalaebs'],
                    metavar='project',
                    help='do not overwrite the project during resync %(default)s')
parser.add_argument('--cfg',
                    default=os.path.join(os.path.dirname(__file__), 
                                         'install.cfg'),
                    help='Config file of the projects [%(default)s]')
args = parser.parse_args()

assert not (args.resync and args.register), \
  "--resync and --register cannot be used simultaneously"

py_scripts_dir = os.path.join(os.path.dirname(sys.executable), 'Scripts')
pip_candidates = (
  os.path.join(py_scripts_dir, 'pip.exe'),
  os.path.join(py_scripts_dir, 'pip2.7.exe'),
  os.path.join(py_scripts_dir, 'pip-2.7-script.py'),
)
for pip in pip_candidates:
  if os.path.isfile(pip):
    break
else:
  print >> sys.stderr, 'Pip not found'
  exit(1)

si = args.si
if not args.register and si is None:  # if args.register, mks not needed at all
  print >> sys.stderr, 'Search for MKS...'
  sys.stderr.flush()
  if os.path.isfile(r'C:\KBApps\Integrity\IntegrityClient11\bin\si.exe'):
    si = r'C:\KBApps\Integrity\IntegrityClient11\bin\si.exe'
  elif os.path.isfile(r'C:\KBApps\Integrity\IntegrityClient10\bin\si.exe'):
    si = r'C:\KBApps\Integrity\IntegrityClient10\bin\si.exe'
  elif os.path.isfile(r'C:\Program Files (x86)\MKS\IntegrityClient\bin\si.exe'):
    si = r'C:\Program Files (x86)\MKS\IntegrityClient\bin\si.exe'
  elif os.path.isfile(r"C:\Program Files\Integrity\IntegrityClient13_2\bin\si.exe"):
      si=r"C:\Program Files\Integrity\IntegrityClient13_2\bin\si.exe"
  else:
    si_name = 'si.exe'
    for find_root in r'C:\KBApps', os.getenv('ProgramFiles(x86)'):
      for root, dirs, files in os.walk(find_root):
        if si_name in files:
          si = os.path.join(root, si_name)
          break
      if si is not None: break
    else:
      print >> sys.stderr, 'MKS is not installed'
      exit(2)
  print >> sys.stderr, '%s used as MKS client' % si
  sys.stderr.flush()

class Project(object):
  si = si
  pip = pip
  @classmethod
  def get_type(cls, name):
    if cls.check(name): return cls
    for sub in cls.__subclasses__():
      if sub.check(name): return sub
      for subsub in sub.__subclasses__():
        if subsub.check(name): return subsub
    raise ValueError('Invalid project type: %s' % name)

  @classmethod
  def check(cls, name):
    return cls.__name__ == name

  def __init__(self, name, prj_dir, scripts=False, branch=None):
    self.name = name
    self.prj = '/'.join([prj_dir, name, name+'.pj'])
    self.branch = branch
    self.scripts = scripts
    self.pip_package_installed = False
    self.python_toolchain_path = r"C:\KBApps\PythonToolchain"
    self.pytch_env_path = r"C:\KBApps\PythonToolchain\dependencies\envs\pytch\python.exe"
    self.sandbox_dir = os.path.join(r"C:\Users\Public", '.pytch_resources')
    self.package_repository_path = os.path.join(self.sandbox_dir, "repository")
    return

  def install(self, overwrite=True):
    if self.is_installed():
      print >> sys.stderr, '%s seems to be already installed' %self.name
      self.resync(overwrite)
    else:
      print >> sys.stderr, 'install %s' %self.name
      os.path.isdir(self.name) or os.mkdir(self.name)
      self.install_for_si()
      self.register()
    return

  def is_installed(self):
    check = os.path.isdir(self.name)
    return check

  def install_for_si(self):
    options = [self.si, 'createsandbox']
    options.extend(self.get_si_options())
    options.append(self.name)

    subprocess.call(options)
    return

  def get_si_options(self):
    options = ['--devpath=%s' % self.branch] if self.branch is not None else []
    options.extend(['-P', self.prj])
    return options

  def install_for_python(self):
    if self.pip.endswith('.py'):
      options = [sys.executable, self.pip, 'install', '-e', self.name]
    else:
      options = [self.pip, 'install', '-e', self.name]

    subprocess.call(options)
    self.reg_scripts()
    return

  def reg_scripts(self):
    if not self.scripts: return

    scripts = os.path.join(os.path.abspath(self.name), 'scripts')
    pth = os.path.join(os.path.dirname(sys.executable), 'Lib', 'site-packages',
                       '%s-scripts.pth' % self.name)
    open(pth, 'w').write(scripts+'\n')
    return

  def install_for_dataeval(self):
    return

  def install_pip_pacakges(self):
    pip_resources = os.path.join(self.package_repository_path, "pip", "pip_req.txt")
    # Pip packages install
    command = "\"" + self.pytch_env_path + "\"" + " -m pip install --no-index --find-links \"" + os.path.dirname(
      pip_resources) + "\" -r \"" + pip_resources + "\""
    subprocess.call(command)

  def resync(self, overwrite):
    self.resync_si(overwrite)
    self.register()
    if not self.pip_package_installed:
      self.install_pip_pacakges()
      self.pip_package_installed = True
    return

  def resync_si(self, overwrite):
    overwrite = '--overwriteChanged' if overwrite else '--nooverwriteChanged'
    options = [
      self.si, 'resync',
      '-S', self.name+'.pj',
      '--overwriteChanged' if overwrite else '--nooverwriteChanged',
    ]
    if self.name != 'pytchresources':
      if not os.path.isdir(self.name):
        os.mkdir(self.name)
      os.chdir(self.name)
      subprocess.call(options)
      os.chdir('..')
    return

  def register(self):
    self.install_for_python()
    self.install_for_dataeval()
    return

class DataevalProject(Project):
  def install_for_dataeval(self):
    options = [sys.executable, 'setup.py', 'install_data']
    options.extend(self.get_install_data_options())

    os.chdir(self.name)
    subprocess.call(options)
    os.chdir('..')
    return

  def get_install_data_options(self):
    return []

class MainProject(DataevalProject):
  dataeval_name = 'aebs'

  def get_install_data_options(self):
    options = ['--dataeval-name', self.dataeval_name]
    return options


class Projects(list):
  section = re.compile('\[(\\w+)\]')
  option = re.compile('(\\w+)\\s*[=:]\\s*(\\S+)')

  def __init__(self, cfg_name):
    """
    Constructor for "Projects" class.
    """
    with open(cfg_name) as cfg:
      section = None
      options = {}
      prj_dirs = {}
      for line in cfg:
        section_match = self.section.search(line)
        option_match = self.option.search(line)
        if section_match:
          if section == 'prj_dir':
            prj_dirs = options
          elif section is not None:
            self._append_project(section, options, prj_dirs)
          options = {}
          section = section_match.group(1)
        elif option_match:
          key, value = option_match.groups()
          options[key] = value
      if section is not None and options:
        self._append_project(section, options, prj_dirs)
    return

  def _append_project(self, section, options, prj_dirs):
    """
    Appends a project to the end of the Projects" list.
    """
    Type = Project.get_type( options.pop('type') )
    prj_dir = prj_dirs[options.pop('prj_dir')]
    try:
      scripts = options.pop('scripts').lower() == 'yes'
    except KeyError:
      scripts = False
    project = Type(section, prj_dir, scripts, **options)
    self.append(project)
    return

if __name__ == '__main__':
  projects = Projects(args.cfg)
  os.chdir(args.dataeval_root)
  for project in projects:
    overwrite = project.name not in args.no_overwrite
    if args.resync:
      project.resync(overwrite)
    elif args.register:
      project.register()
    else:
      project.install(overwrite=overwrite)

  subprocess.call([sys.executable, '-m', 'scan'])
