#!/usr/bin/env python
import os
import sys
import inspect
from distutils.cmd import Command
import setuptools, platform
import setuptools
from setuptools.command.test import test as TestCommand
from setuptools import setup
from setuptools.command.install import install 

MAIN_PACKAGE = "iggytools"
DESCRIPTION = "Genome and database downloader"
LICENSE = "GPLv3"
URL = "http://github.com/harvardinformatics/iggytools"
AUTHOR = "Chris Williams"
EMAIL = "wilcliams@gmail.com"

COVERAGE_XML = False
COVERAGE_HTML = False
JUNIT_XML = False

CLASSIFIERS = [ 'Programming Language :: Python',
                'Development Status :: 4 - Beta',
                'Intended Audience :: Developers',
                'Operating System :: OS Independent',
                'Topic :: Scientific/Engineering :: Bio-Informatics',
                'Natural Language :: English' ]

__location__ = os.path.join(os.getcwd(), os.path.dirname(
    inspect.getfile(inspect.currentframe())))

def read(fname):
    return open(os.path.join(__location__, fname)).read()

def get_install_requirements(path):
    content = open(os.path.join(__location__, path)).read()
    return [req for req in content.splitlines() if req != '']

def get_3p_dirname():
    system = platform.system()
    if system == 'Linux':
        return 'linux-x86_64'
    elif system == 'Windows':
        return 'win64'
    elif system == 'Darwin':
        return 'macos-x86_64'
    else:
        raise Exception('Unrecognized system: %s' % system)

class PyTest(TestCommand):
    user_options = [("cov=", None, "Run coverage"),
                    ("cov-xml=", None, "Generate junit xml report"),
                    ("cov-html=", None, "Generate junit html report"),
                    ("junitxml=", None, "Generate xml of test results")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.cov = None
        self.cov_xml = False
        self.cov_html = False
        self.junitxml = None

    def finalize_options(self):
        TestCommand.finalize_options(self)
        if self.cov is not None:
            self.cov = ["--cov", self.cov, "--cov-report", "term-missing"]
            if self.cov_xml:
                self.cov.extend(["--cov-report", "xml"])
            if self.cov_html:
                self.cov.extend(["--cov-report", "html"])
        if self.junitxml is not None:
            self.junitxml = ["--junitxml", self.junitxml]

    def run_tests(self):
        try:
            import pytest
        except:
            raise RuntimeError("py.test is not installed, "
                               "run: pip install pytest")
        params = {"args": self.test_args}
        if self.cov:
            params["args"] += self.cov
            params["plugins"] = ["cov"]
        if self.junitxml:
            params["args"] += self.junitxml
        errno = pytest.main(**params)
        sys.exit(errno)

def sphinx_builder():
    try:
        from sphinx.setup_command import BuildDoc
    except ImportError:
        class NoSphinx(Command):
            user_options = []
            def initialize_options(self):
                raise RuntimeError("Sphinx documentation is not installed, "
                                   "run: pip install sphinx")
        return NoSphinx
    class BuildSphinxDocs(BuildDoc):
        def run(self):
            if self.builder == "doctest":
                import sphinx.ext.doctest as doctest
                # Capture the DocTestBuilder class in order to return the total
                # number of failures when exiting
                ref = capture_objs(doctest.DocTestBuilder)
                BuildDoc.run(self)
                errno = ref[-1].total_failures
                sys.exit(errno)
            else:
                BuildDoc.run(self)
    return BuildSphinxDocs

class ObjKeeper(type):
    instances = {}
    def __init__(cls, name, bases, dct):
        cls.instances[cls] = []
    def __call__(cls, *args, **kwargs):
        cls.instances[cls].append(super(ObjKeeper, cls).__call__(*args, **kwargs))
        return cls.instances[cls][-1]

def capture_objs(cls):
    from six import add_metaclass
    module = inspect.getmodule(cls)
    name = cls.__name__
    keeper_class = add_metaclass(ObjKeeper)(cls)
    setattr(module, name, keeper_class)
    cls = getattr(module, name)
    return keeper_class.instances[cls]

def setup_package():
    # Set __version__
    exec(open('iggytools/version.py').read())  

    # Assemble additional setup commands
    cmdclass = dict()
    cmdclass['doctest'] = sphinx_builder()
    cmdclass['docs'] = sphinx_builder()
    cmdclass['test'] = PyTest

    # Some helper variables
    docs_path = os.path.join(__location__, "docs")
    docs_build_path = os.path.join(docs_path, "_build")
    install_reqs = get_install_requirements("requirements.txt")

    command_options = {
        'docs': {'project': ('setup.py', MAIN_PACKAGE),
                 'version': ('setup.py', __version__.split('-', 1)[0]),
                 'release': ('setup.py', __version__),
                 'build_dir': ('setup.py', docs_build_path),
                 'config_dir': ('setup.py', docs_path),
                 'source_dir': ('setup.py', docs_path)},
        'doctest': {'project': ('setup.py', MAIN_PACKAGE),
                    'version': ('setup.py', __version__.split('-', 1)[0]),
                    'release': ('setup.py', __version__),
                    'build_dir': ('setup.py', docs_build_path),
                    'config_dir': ('setup.py', docs_path),
                    'source_dir': ('setup.py', docs_path),
                    'builder': ('setup.py', 'doctest')},
        'test': {'test_suite': ('setup.py', 'tests'),
                 'cov': ('setup.py', 'iggytools')}}
    if JUNIT_XML:
        command_options['test']['junitxml'] = ('setup.py', 'junit.xml')
    if COVERAGE_XML:
        command_options['test']['cov_xml'] = ('setup.py', True)
    if COVERAGE_HTML:
        command_options['test']['cov_html'] = ('setup.py', True)

    setup(name=MAIN_PACKAGE,
          version=__version__,
          url=URL,
          description=DESCRIPTION,
          author=AUTHOR,
          author_email=EMAIL,
          license=LICENSE,
          long_description=read('description.txt'),
          classifiers=CLASSIFIERS,
          test_suite='tests',
          packages=setuptools.find_packages(exclude=['tests', 'tests.*']),
          package_data={'iggytools': ['config/preferenceTemplates/*.yaml',
                                      'thirdparty/%s/bowtie2-2.2.4/bowtie2*' % get_3p_dirname()]},
          include_package_data=True,
          install_requires=install_reqs,
          setup_requires=['six'],
          cmdclass=cmdclass,
          tests_require=['pytest-cov', 'pytest'],
          command_options=command_options,
          scripts = ['iggytools/bin/iggyref_setup', 'iggytools/bin/iggyref_update'],
          zip_safe = False
          )

if __name__ == "__main__":
    setup_package()

