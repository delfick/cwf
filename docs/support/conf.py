"""
    Options for sphinx
    Add project specific options to conf.py in the root folder
"""
import cloud_sptheme
import sys, os

# Add _ext and support folders to sys.path
this_dir = os.path.abspath(os.path.dirname(__file__))
build_dir = os.path.join(this_dir, "build")
theme_dir = os.path.join(this_dir, "theme")

sys.path.extend([this_dir, os.path.join(this_dir, 'ext')])

extensions = ['sphinx.ext.autodoc', 'sphinx.ext.viewcode', 'nav']
html_theme_path = [theme_dir, cloud_sptheme.get_theme_dir()]
exclude_patterns = [build_dir]

master_doc = 'index'
source_suffix = '.rst'

html_theme = 'navcloud'
pygments_style = 'pastie'

# Add options specific to this project
execfile(os.path.join(this_dir, '../conf.py'), globals(), locals())
