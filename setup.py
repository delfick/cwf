from setuptools import setup, find_packages

setup(
      name = "cwf"
    , version = "1.0"
    , packages = ['cwf'] + ['cwf.%s' % pkg for pkg in find_packages('cwf')]
    , include_package_data = True

    , entry_points =
      { 'console_scripts' :
        [ 'cwf-manager = cwf.bin.manager:main'
        , 'cwf-debugger = cwf.bin.debugger_cli:main'
        ]
      }

    , install_requires =
        [ 'werkzeug'
        , 'paste'
        ]

    # metadata for upload to PyPI
    , url = "https://cwf.readthedocs.org"
    , author = "Stephen Moore"
    , author_email = "stephen@delfick.com"
    , description = "Library that sits between django and a website"
    , license = "WTFPL"
    , keywords = "django website"
    )
