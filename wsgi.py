import os
import sys
from django.core.handlers.wsgi import WSGIHandler

sys.path.append(os.path.abspath(os.path.dirname(__file__)))
os.environ["DJANGO_SETTINGS_MODULE"]="mm.settings"
os.environ["PYTHON_EGG_CACHE"]='/tmp/.python-eggs'
application=WSGIHandler()
