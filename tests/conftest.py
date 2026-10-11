import os

import django


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "debtly.settings")
django.setup()
