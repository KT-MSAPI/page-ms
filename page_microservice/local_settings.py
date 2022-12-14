# This file is exec'd from settings.py, so it has access to and can
# modify all the variables in settings.py.
import os
DEBUG = True

# Make these unique, and don't share it with anybody.
SECRET_KEY = "=1&6^m2pi0ots3$s$csporp6zs-j@4hmm_7(7le4)u!ahti6xu"
NEVERCACHE_KEY = "8i0s&+%@j@dj09hc1#iv7j-4z#l#(_gk+_f&a^23bg@x%i0p&h"

DATABASES = {
    "default": {
        # Ends with "postgresql_psycopg2", "mysql", "sqlite3" or "oracle".
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        # DB name or path to database file if using sqlite3.
        "NAME": "pagems",
        # Not used with sqlite3.
        "USER": "kultivate",
        # Not used with sqlite3.
        "PASSWORD": "kultivate",
        # Set to empty string for localhost. Not used with sqlite3.
        #"HOST": "$REMOTE_POSTGRES_IP",
        "HOST": "kt-prod-db.cgsoupmv1lrk.ap-south-1.rds.amazonaws.com",
        # Set to empty string for default. Not used with sqlite3.
        "PORT": "5432",
    }
}

# Allowed development hosts
ALLOWED_HOSTS = ["localhost", "127.0.0.1", "::1", '*']

# PROJECT_ROOT = '/opt/farmer_ms_assets/'

#static & Media 
STATIC_URL = '/static/'
MEDIA_URL = STATIC_URL + '/media/' 
DATA_DIR = '/opt/pagems-assets/'
STATIC_ROOT = os.path.join(DATA_DIR, STATIC_URL.strip("/"))
MEDIA_ROOT = os.path.join(DATA_DIR, MEDIA_URL.strip("/"))


# STATICFILES_DIRS = (
#     os.path.join('/opt/static/', 'pincode_admin', 'static'),
# )