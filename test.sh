#! /bin/bash
export NOSE_NOY_EXTRA_IMPORTS="from django.test import TestCase"
export NOSE_NOY_DEFAULT_KLS="TestCase"
python manage.py test $@
