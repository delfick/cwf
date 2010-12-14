#! /bin/bash
# Example test.sh
export PYTHONPATH=$PYTHONPATH:$WEBSETTINGS/helpers
export NOSE_NOY_EXTRA_IMPORTS="from django.test import TestCase"
export NOSE_NOY_DEFAULT_KLS="TestCase"
django-manage.sh test --settings=cwf.helpers.testSettings
