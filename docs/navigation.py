"""
    toplinks for the navigation for the docs.
    Look at _ext/nav.py to see how this content is added to the context when rendering the docs.

    Just edit toplinks to be a list of tuples representing each top navigation item in the site.
    Where each tuple is (name, url, condition)

    Name: Name that's used for the link
    Url: The page that the link takes you to relative to docs, please lead this with a slash
    Condition: Regular expression that must match the path of the page being viewed for the button to be shown as selected
"""
toplinks = [
          ('Overview',      '/index.html',              '^(index|tests|installation)$')
        , ('Sections',      '/sections/index.html',     '^sections')
        , ('Views',         '/views/index.html',        '^views')
        , ('Splitter',      '/splitter/index.html',     '^splitter')
        , ('Binaries',      '/bin/index.html',          '^bin')
        , ('Admin',         '/admin/index.html',        '^admin')
        , ('Template Tags', '/templatetags/index.html', '^templatetags')
        , ('Templates',     '/templates/index.html',    '^templates')
        ]
