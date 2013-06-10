from defaults import *

DEBUG = True

TEMPLATE_DEBUG = DEBUG

INTERNAL_IPS = ('127.0.0.1', )

# # DJANGO-PDB
# INSTALLED_APPS += ('django_pdb', )
# MIDDLEWARE_CLASSES += ('django_pdb.middleware.PdbMiddleware', )

# # DJANGO DEBUG TOOLBAR
# MIDDLEWARE_CLASSES = ('debug_toolbar.middleware.DebugToolbarMiddleware', ) + MIDDLEWARE_CLASSES
# INSTALLED_APPS += (
#     'django.contrib.admin',
#     'debug_toolbar',
# )
# DEBUG_TOOLBAR_CONFIG = {
#     'INTERCEPT_REDIRECTS': False,
# }

# # Django coverage settings
# INSTALLED_APPS += ('django_coverage', )
# TEST_RUNNER = 'config.settings.testrunner.ProjectCoverageRunner'
# COVERAGE_MODULE_EXCLUDES = (
#     'tests$', 'settings$', 'urls$', 'locale$', 'migrations', 'fixtures',
#     'debug_toolbar', 'admin', 'django_pdb', 'factories$',
# )
# COVERAGE_MODULE_EXCLUDES += BASE_APPS
# COVERAGE_REPORT_HTML_OUTPUT_DIR = os.path.join(os.path.abspath("%s/.." % PROJECT_DIR), "coverage")
