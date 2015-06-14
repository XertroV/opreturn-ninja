import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.md')) as f:
    README = f.read()
with open(os.path.join(here, 'CHANGES.txt')) as f:
    CHANGES = f.read()

requires = [
    'pyramid',
    'pyramid_chameleon',
    'pyramid_debugtoolbar',
    'pyramid_tm',
    'waitress',
    #'python-bitcoinlib',
    'bitcoin-python'
    ]

setup(name='op-return-ninja',
      version='0.0',
      description='op-return-ninja',
      long_description=README + '\n\n' + CHANGES,
      classifiers=[
        "Programming Language :: Python",
        "Framework :: Pyramid",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        ],
      author='',
      author_email='',
      url='',
      keywords='web wsgi bfg pylons pyramid',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      test_suite='opreturnninja',
      install_requires=requires,
      entry_points="""\
      [paste.app_factory]
      main = opreturnninja:main
      [console_scripts]
      initialize_op-return-ninja_db = opreturnninja.scripts.initializedb:main
      """,
      )
