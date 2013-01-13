.. _installation:

Installation
============

As with any python project, it is recommended you use virtualenv.

You may setup virtualenv as you like, I use virtualenvwrapper:

.. code-block:: bash

    $ sudo pip install virtualenvwrapper

    # Change where your virtualenvs are
    $ echo "export WORKON_HOME=$HOME/venv" >> ~/.zshrc

    # Make sure your ~/.bashrc or ~/.zshrc has the virtualenvwrapper script
    $ echo "[[ -s /usr/local/bin/virtualenvwrapper.sh ]] && source /usr/local/bin/virtualenvwrapper.sh" >> ~/.zshrc

    $ source ~/.zshrc

    # Create the virtualenv
    $ mkvirtualenv cwf

Once your virtualenv is created, then you activate it before doing anything
in that virtualenv:

.. code-block:: bash

    # If you are using vanilla virtualenv
    $ source <venv_path>/bin/activate

    # Or if you are using virtualenvwrapper
    $ workon cwf

Once you're inside your virtualenv
(or without that if you are installing cwf system wide):

If you want to install it from pypi, then do the following:

.. code-block:: bash

    $ pip install cwf

Otherwise, if you are installing it from source

.. code-block:: bash

    $ pip install .

If you're developing for cwf, then it's recommended you do that with the "-e"
flag (behaves like ``python setup.py develop``):

.. code-block:: bash

    # If you want to constantly make changes to cwf
    # Remove the need to keep reinstalling it
    $ pip install -e .
