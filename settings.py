#########################
# settings.py
#
# This is a Django settings file with debug set to False

import os
HOMEDIR = os.sep.join(__file__.split('/')[:3])
PROJECTDIR = os.sep.join(__file__.split('/')[:-1])

TEMPLATE_DEBUG = DEBUG = False

# Exposing database details is a security hole, so leave them blank here.
DATABASE_ENGINE = 'sqlite3'
DATABASE_NAME = ''
DATABASE_USER = ''
DATABASE_PASSWORD = ''
DATABASE_HOST = ''
DATABASE_PORT = ''
SECRET_KEY = ''

ROOT_URLCONF = 'templates.urls'

########################
###
###   RANDOM
###
########################

LANGUAGE_CODE = 'en-us'
LOG_FILE = 'messages.log'
TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'
NOSE_ARGS = [ '--with-spec'
            , '--spec-color'
            , '--with-noy'
            , '--noy-ignore-kls=TestCase'
            , '--noy-ignore-kls=TransactionTestCase'
            ]

########################
###
###   INCLUSIONS
###
########################

INSTALLED_APPS = ( 'views'
                 , 'django_nose'
                 , 'cwf_new'
                 )

TEMPLATE_DIRS = (
	'%s/templates' % PROJECTDIR,
	'%s/menus/templates' % PROJECTDIR
)

