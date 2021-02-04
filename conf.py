project = 'Bookings API'
copyright = '2020, Chris Gough'
author = 'Chris Gough'
release = '0.1'
extensions = [
    'sphinxcontrib.plantuml',
    'sphinxcontrib.httpdomain'
]
templates_path = ['_templates']
exclude_patterns = [
    '_build', 'Thumbs.db', '.DS_Store',
    '.venv', '.git',
]
html_theme = 'alabaster'
html_static_path = ['_static']

# kludge for readthedocs.io
master_doc = 'index'
