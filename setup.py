from setuptools import setup, find_packages

setup(
      name = "cwf"
    , version = "1.0"
    , packages = ['cwf'] + ['cwf.%s' % pkg for pkg in find_packages('cwf')]
    , install_requires =
      [
      ]

    , entry_points =
      { 'console_scripts' :
        [ 'cwf-manager = cwf.bin.manager:main'
        , 'cwf-debugger = cwf.bin.debugger_cli:main'
        ]
      }

    # metadata for upload to PyPI
    , author = "Stephen Moore"
    , author_email = "stephen@delfick.com"
    , description = "Library that sits between django and a website"
    , license = "WTFPL"
    , keywords = "django website"
    )
