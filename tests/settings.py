#########################
# settings.py
#
# This is a Django settings file with debug set to False

import os
this_dir = os.path.dirname(__file__)

APPEND_SLASH = True
TEMPLATE_DEBUG = DEBUG = False

# Exposing database details is a security hole, so leave them blank here.
DATABASES = {
    'default': {
          'ENGINE': 'django.db.backends.sqlite3'
        , 'NAME': ''
        , 'USER': ''
        , 'PASSWORD': ''
        , 'HOST': ''
        , 'PORT': ''
        }
    }

ROOT_URLCONF = 'tests.urls'

########################
###
###   RANDOM
###
########################

LANGUAGE_CODE = 'en-us'
LOG_FILE = 'messages.log'
TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'
NOSE_ARGS = [ 
      '--with-spec'
    , '--spec-color'
    , '--with-noy'
    , '--pdb'
    , '--noy-ignore-kls=TestCase'
    , '--noy-ignore-kls=TransactionTestCase'
    , '--noy-default-kls=TestCase'
    ]

########################
###
###   INCLUSIONS
###
########################

INSTALLED_APPS = (
      'cwf'
    , 'django_nose'
    )

TEMPLATE_DIRS = (
	  os.path.join(this_dir, 'templates')
	, os.path.join(this_dir, '..', 'cwf', 'templates')
    )
