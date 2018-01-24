try:
    import sphinx_rtd_theme
except ImportError:
    sphinx_rtd_theme = None

master_doc = 'index'

if sphinx_rtd_theme:
    html_theme = "sphinx_rtd_theme"
    html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]
