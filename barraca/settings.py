"""
Django settings for barraca project.

Generated by 'django-admin startproject' using Django 4.2.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""

from dotenv import load_dotenv
from pathlib import Path
import os
import datetime
import django_heroku
import dj_database_url

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv()

# LOGS_DIR = os.path.join(BASE_DIR, 'logs')
# if not os.path.exists(LOGS_DIR):
#     os.makedirs(LOGS_DIR)

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-)l-r0e3802bh)^4v)5rerq#x+8r=zx=t593=u^l4_u(ee)8^wx'

# SECURITY WARNING: don't run with debug turned on in production!
#DEBUG = False

if os.getenv('DJANGO_DEBUG') == 'True':
    DEBUG = True
else:
    DEBUG = False

ALLOWED_HOSTS = ['*']

# Application definition

INSTALLED_APPS = [
    #'jazzmin',
    #'admin_reorder',
    'django_feather',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    #CELERY
    'django_celery_beat',
    'django_celery_results',
    #APPS
    'core',
    'record_management',
    'frontend',
    'admin_dashboard',
    'appointment_management',
    'customer_dashboard',
    'billing_management',
    'inventory_services_management', #PROXY ONLY
    'inventory',
    'services',
    'rest_api',
    #STORAGES
    'storages',
    'rest_framework',
    'rest_framework.authtoken',
    'rest_framework.throttling',
    'nested_admin',
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.ScopedRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'get_pet': '5/minute',
        'mobile_login': '5/minute',
        'submit_consultation': '5/minute',
    },
    'EXCEPTION_HANDLER': 'rest_api.rest_exceptions.custom_exception_handler',
}

# ADMIN_REORDER = (
#     {'app': 'appointment_management', 'label': 'Appointment Management'},
#     {'app': 'billing_management', 'label': 'Billing Management'},
#     {'app': 'inventory_services_management', 'label': 'Inventory & Services Management'},
#     {'app': 'record_management', 'label': 'Record Management'},
#     {'app': 'core', 'label': 'Core'},
#     {'app': 'django_celery_beat', 'label': 'Celery Beat'},
#     {'app': 'django_celery_results', 'label': 'Celery Results'},
#     {'app': 'authtoken', 'label': 'Token'},
#     {'app': 'rest_framework.throttling.ScopedRateThrottle', 'label': 'Auth'},
#     {'app': 'django', 'label': 'Sessions'},
# )

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    #'admin_reorder.middleware.ModelAdminReorder',
    #'core.middleware.SessionDisplayMiddleware',
    # 'core.middleware.MinifyHTMLMiddleware',
]

# WhiteNoise Configuration
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

WHITENOISE_ROOT = os.path.join(BASE_DIR, 'media')
WHITENOISE_MAX_AGE = 60 * 60 * 24 * 30  # Cache for 30 days

ROOT_URLCONF = 'barraca.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'barraca.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases


# HEROKU DEPLOYMENT
# DATABASES = {
#     'default': dj_database_url.config(default=os.environ.get('DATABASE_URL'))
# }

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv("DB_NAME"),
        'USER': os.getenv("DB_USER"),
        'PASSWORD': os.getenv("DB_PASSWORD"),
        'HOST': os.getenv("DB_HOST"),
        'PORT': os.getenv("PORT"),
    }
}



# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Manila'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
]

if not DEBUG:
    AWS_ACCESS_KEY_ID = os.getenv('BUCKETEER_AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.getenv('BUCKETEER_AWS_SECRET_ACCESS_KEY')
    AWS_STORAGE_BUCKET_NAME = os.getenv('BUCKETEER_BUCKET_NAME')
    AWS_S3_REGION_NAME = os.getenv('BUCKETEER_AWS_REGION')
    AWS_S3_SIGNATURE_VERSION = 's3v4'
    AWS_S3_FILE_OVERWRITE = False
    AWS_DEFAULT_ACL = None
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    MEDIA_URL = f'https://{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com/public/'
else:
    MEDIA_URL = '/media/'
    MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

STATIC_URL = '/static/'

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_URL = '/login/'
LOGOUT_REDIRECT_URL = 'home'

django_heroku.settings(locals())

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}

SEMAPHORE_API_KEY = os.getenv("SEMAPHORE_API_KEY")

SESSION_COOKIE_NAME = 'sessionid'
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
#SESSION_COOKIE_AGE = 1200

# Celery settings
CELERY_BROKER_URL = os.environ.get("REDIS_URL", "redis://127.0.0.1:6379")
#CELERY_RESULT_BACKEND = os.environ.get("REDIS_URL", "redis://127.0.0.1:6379")
CELERY_RESULT_BACKEND = 'django-db'
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TASK_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE
#CELERY_SEND_EVENTS = True

# from datetime import timedelta

# CELERY_BEAT_SCHEDULE = {
#     'print_hello_world_task': {
#         'task': 'core.tasks.print_hello_world',
#         'schedule': 30.0,
#     },
# }

OTP_EXPIRATION_MINUTES = 5

MAX_APPOINTMENTS = 8

AUTHENTICATION_BACKENDS = ['django.contrib.auth.backends.AllowAllUsersModelBackend']

# JAZZMIN_SETTINGS = {
#     # title of the window (Will default to current_admin_site.site_title if absent or None)
#     "site_title": "Barraca Superadmin",

#     # Title on the login screen (19 chars max) (defaults to current_admin_site.site_header if absent or None)
#     "site_header": "Barraca",

#     # Title on the brand (19 chars max) (defaults to current_admin_site.site_header if absent or None)
#     "site_brand": "Barraca",

#     # Logo to use for your site, must be present in static files, used for brand on top left
#     "site_logo": 'images/billing.png',

#     # Logo to use for your site, must be present in static files, used for login form logo (defaults to site_logo)
#     "login_logo": None,

#     # Logo to use for login form in dark themes (defaults to login_logo)
#     "login_logo_dark": None,

#     # CSS classes that are applied to the logo above
#     "site_logo_classes": "img-circle",

#     # Relative path to a favicon for your site, will default to site_logo if absent (ideally 32x32 px)
#     "site_icon": 'images/favicon.webp',

#     # Welcome text on the login screen
#     "welcome_sign": "Welcome to Barraca Superadmin",

#     # Copyright on the footer
#     "copyright": "Barraca Veterinary Clinic",

#     # List of model admins to search from the search bar, search bar omitted if excluded
#     # If you want to use a single search field you dont need to use a list, you can use a simple string 
#     "search_model": None,

#     # Field name on user model that contains avatar ImageField/URLField/Charfield or a callable that receives the user
#     "user_avatar": None,

#     ############
#     # Top Menu #
#     ############

#     # Links to put along the top menu
#     "topmenu_links": [

#         # Url that gets reversed (Permissions can be added)
#         {"name": "Home",  "url": "admin:index", "permissions": ["auth.view_user"]},

#         # App with dropdown menu to all its models pages (Permissions checked against models)
#         {"app": None},
#     ],

#     #############
#     # User Menu #
#     #############

#     # Additional links to include in the user menu on the top right ("app" url type is not allowed)
#     "usermenu_links": [
#         {"name": "Visit Site", "url": "/", "icon": "fas fa-home"},
#         {"name": "Visit Normal Admin", "url": "/admin/", "icon": "fas fa-link"},
#     ],

#     #############
#     # Side Menu #
#     #############

#     # Whether to display the side menu
#     "show_sidebar": True,

#     # Whether to aut expand the menu
#     "navigation_expanded": True,

#     # Hide these apps when generating side menu e.g (auth)
#     "hide_apps": ["auth", "auth.user", "auth.Group"],

#     # Hide these models when generating side menu (e.g auth.user)
#     "hide_models": [],

#     # List of apps (and/or models) to base side menu ordering off of (does not need to contain all apps/models)
#     "order_with_respect_to": ["auth", "appointment_management", "billing_management", "inventory_services_management", "record_management"],

#     # Custom icons for side menu apps/models See https://fontawesome.com/icons?d=gallery&m=free&v=5.0.0,5.0.1,5.0.10,5.0.11,5.0.12,5.0.13,5.0.2,5.0.3,5.0.4,5.0.5,5.0.6,5.0.7,5.0.8,5.0.9,5.1.0,5.1.1,5.2.0,5.3.0,5.3.1,5.4.0,5.4.1,5.4.2,5.13.0,5.12.0,5.11.2,5.11.1,5.10.0,5.9.0,5.8.2,5.8.1,5.7.2,5.7.1,5.7.0,5.6.3,5.5.0,5.4.2
#     # for the full list of 5.13.0 free icon classes
#     "icons": {
#         "auth": "fas fa-users-cog",
#         "auth.user": "fas fa-user",
#         "auth.Group": "fas fa-users",
#         "appointment_management.Appointment": "fas fa-calendar-alt",
#         "appointment_management.MaximumAppointment": "fas fa-hashtag",
#         "appointment_management.DateSlot": "fas fa-splotch",
#         "appointment_management.DoctorSchedule": "fas fa-stethoscope",
#         "billing_management.Billing": "fas fa-file-invoice-dollar",
#         "inventory_services_management.Product": "fas fa-boxes",
#         "inventory_services_management.Service": "fas fa-stethoscope",
#         "inventory_services_management.ProductType": "fas fa-layer-group",
#         "record_management.Client": "fas fa-database",
#         "record_management.Pet": "fas fa-dog",
#         "record_management.User": "fas fa-user",
#         "record_management.Group": "fas fa-users",
#         "django_celery_beat.PeriodicTask": "fas fa-clock",
#         "django_celery_beat.IntervalSchedule": "fas fa-paperclip",
#         "django_celery_beat.CrontabSchedule": "fas fa-calendar-alt",
#         "django_celery_results.TaskResult": "fas fa-tasks",
#         "core.Notification": "fas fa-bell",
#         "core.SMSLogs": "fas fa-sms",
#         "django.contrib.admin.LogEntry": "fas fa-bell",
#     },
#     # Icons that are used when one is not manually specified
#     "default_icon_parents": "fas fa-chevron-circle-right",
#     "default_icon_children": "fas fa-circle",

#     #################
#     # Related Modal #
#     #################
#     # Use modals instead of popups
#     "related_modal_active": False,

#     #############
#     # UI Tweaks #
#     #############
#     # Relative paths to custom CSS/JS scripts (must be present in static files)
#     "custom_css": None,
#     "custom_js": None,
#     # Whether to link font from fonts.googleapis.com (use custom_css to supply font otherwise)
#     "use_google_fonts_cdn": True,
#     # Whether to show the UI customizer on the sidebar
#     "show_ui_builder": False,

#     ###############
#     # Change view #
#     ###############
#     # Render out the change view as a single form, or in tabs, current options are
#     # - single
#     # - horizontal_tabs (default)
#     # - vertical_tabs
#     # - collapsible
#     # - carousel
#     "changeform_format": "horizontal_tabs",
#     # override change forms on a per modeladmin basis
#     "changeform_format_overrides": {"auth.user": "collapsible", "auth.group": "vertical_tabs"},
# }

# JAZZMIN_UI_TWEAKS = {
#     "navbar_small_text": True,
#     "footer_small_text": True,
#     "body_small_text": False,
#     "brand_small_text": True,
#     "brand_colour": "navbar-dark",
#     "accent": "accent-navy",
#     "navbar": "navbar-white navbar-light",
#     "no_navbar_border": True,
#     "navbar_fixed": False,
#     "layout_boxed": False,
#     "footer_fixed": False,
#     "sidebar_fixed": False,
#     "sidebar": "sidebar-dark-navy",
#     "sidebar_nav_small_text": True,
#     "sidebar_disable_expand": True,
#     "sidebar_nav_child_indent": False,
#     "sidebar_nav_compact_style": True,
#     "sidebar_nav_legacy_style": False,
#     "sidebar_nav_flat_style": False,
#     "theme": "default",
#     "dark_mode_theme": None,
#     "button_classes": {
#         "primary": "btn-outline-primary",
#         "secondary": "btn-outline-secondary",
#         "info": "btn-info",
#         "warning": "btn-warning",
#         "danger": "btn-danger",
#         "success": "btn-success"
#     },
#     "actions_sticky_top": False
# }