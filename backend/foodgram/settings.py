import os

#from dotenv import load_dotenv

#load_dotenv()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SECRET_KEY = 'ru=6wtyt+e09%4o#m7h%xut9exodi3i3&l^*2#^hf%*((b^al1'
#SECRET_KEY = os.getenv('SECRET_KEY', default='testkey')

DEBUG = True

ALLOWED_HOSTS = ['*']


INSTALLED_APPS = [
    'api.apps.ApiConfig',
    'recipes.apps.RecipesConfig',
    'users.apps.UsersConfig',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'sorl.thumbnail',
    'rest_framework',
    'rest_framework.authtoken',
    'django_filters',
    'djoser',
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

ROOT_URLCONF = 'foodgram.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'foodgram.wsgi.application'


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# DATABASES = {
#     'default': {
#         'ENGINE': os.getenv('DB_ENGINE', default='django.db.backends.postgresql'),
#         'NAME': os.getenv('DB_NAME', default='postgres'),
#         'USER': os.getenv('POSTGRES_USER', default='postgres'),
#         'PASSWORD': os.getenv('POSTGRES_PASSWORD', default='postgres'),
#         'HOST': os.getenv('DB_HOST', default='db'),
#         'PORT': os.getenv('DB_PORT', default='5432')
#     }
# }


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


LANGUAGE_CODE = 'ru-RU'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")


REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ],

    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
    ),

    'DEFAULT_PAGINATION_CLASS':
        'api.pagination.PagePagination',
        'PAGE_SIZE': 6,
}

DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

DJOSER = {
    'LOGIN_FIELD': "email",
    'HIDE_USERS': False,
    "SERIALIZERS": {
        "user": "api.serializers.CustomUserSerializer",
        "current_user": "api.serializers.CustomUserSerializer",
        "user_create": "api.serializers.CustomUserCreateSerializer",
    },
    'PERMISSIONS': {
        'user': ['rest_framework.permissions.IsAuthenticated'],
        'user_list': ['rest_framework.permissions.AllowAny'],
        'token_destroy': ['rest_framework.permissions.IsAuthenticated'],
    },
}
