import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '...'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True


ALLOWED_HOSTS = ["*"]


# Application definition

INSTALLED_APPS = [
    'jazzmin.apps.JazzminConfig',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # My Apps
    'home.apps.HomeConfig',
    'accounts.apps.AccountsConfig',
    'shop.apps.ShopConfig',
    'blog.apps.BlogConfig',
    'django_cleanup.apps.CleanupConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'Book_Shop.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR / 'templates',
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'Book_Shop.context.site_settings'
            ],
        },
    },
]

WSGI_APPLICATION = 'Book_Shop.wsgi.application'


# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
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

AUTH_USER_MODEL = "accounts.User"

# Internationalization
LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static')
]

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(
    BASE_DIR, 'media'
)

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Email
EMAIL_BACKEND       = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST          = 'smtp.gmail.com'
EMAIL_PORT          = 587
EMAIL_USE_TLS       = True
EMAIL_HOST_USER     = '...'
EMAIL_HOST_PASSWORD = '...'
DEFAULT_FROM_EMAIL  = EMAIL_HOST_USER

# stripe test
STRIPE_SECRET_KEY      = '...'
STRIPE_PUBLISHABLE_KEY = '...'

#Jazzmin settings
JAZZMIN_SETTINGS = {
    'site_title'   : 'Bookim Admin',
    'site_header'  : 'Bookim Admin',
    'site_brand'   : 'Bookim',
    'site_logo'    : 'assets/img/favicon.png',
    'login_logo'   : 'assets/img/logo/logo.svg',
    'welcome_sign' : 'Welcome to Bookim Admin Panel.',
}

JAZZMIN_UI_TWEAKS = {
    'theme'                    : 'flatly',
    'primary'                  : 'success',
    'accent'                   : 'teal',
    'navbar'                   : 'navbar-light',
    'sidebar'                  : 'sidebar-dark-success',
    'sidebar_nav_flat_style'   : True,
    'sidebar_nav_compact_style': False,
    'body_small_text'          : False,
    'footer_small_text'        : True,
    'sidebar_disable_expand'   : False,
}
