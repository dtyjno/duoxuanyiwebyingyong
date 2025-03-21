"""
Django settings for mysite project.

Generated by 'django-admin startproject' using Django 5.1.6.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.1/ref/settings/
"""

from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure--de$mawn8*r2#!$1&389d7yt%an+m)+owt)gf*zm8-p@%+j19('

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# ALLOWED_HOSTS = []
ALLOWED_HOSTS = ['*'] # 允许全部IP访问项目

# CORS_ALLOW_HEADERS = "*"

# Application definition

INSTALLED_APPS = [
    'polls.apps.PollsConfig',
    'captcha',
    'rest_framework',
    'rest_framework.authtoken',
    'daphne', # 增加daphne这一项，而且必须在channels之前,使用ASGI
    'channels', # 
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'corsheaders', # 注册app corsheaders
]

# MIDDLEWARE_CLASSES = [
#     'corsheaders.middleware.CorsMiddleware', # 加入中间键 位置必须在这里 不能在其他位置
#     'django.middleware.security.SecurityMiddleware',
#     'django.contrib.sessions.middleware.SessionMiddleware',
#     'django.middleware.common.CommonMiddleware',

#     # 'django.middleware.csrf.CsrfViewMiddleware', 
#     'django.contrib.auth.middleware.AuthenticationMiddleware',
#     'django.contrib.messages.middleware.MessageMiddleware',
#     'django.middleware.clickjacking.XFrameOptionsMiddleware',
# ]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware', # 加入中间键
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware', # CSRF中间件 
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'mysite.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['frontend/dist'], # 指定前端模板文件夹
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

WSGI_APPLICATION = 'mysite.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'zh-hans' #'en-us' #~'zh-CN'~

TIME_ZONE = 'Etc/GMT-8' #'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


REST_FRAMEWORK = {
    # settings.py

    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',  # 启用Token认证
        'rest_framework.authentication.SessionAuthentication',
    ],
    # 使用DRF的Token过期设置（需自定义）

    'DEFAULT_AUTH_TOKEN_CLASSES': [
        'polls.authentication.ExpiringTokenAuthentication'
    ],
    'TOKEN_EXPIRE_HOURS': 72,



    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10
}

# 允许所有 域名/IP 跨域
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOWED_ORIGINS = [
    "http://localhost",
    "http://localhost:5173",
    "http://127.0.0.1:5173",        # 前端开发地址
    "http://127.0.0.1:8000",       # 本地开发地址
    "http://localhost:8000",       # 本地开发地址
    # "https://deepseek.hdu.edu.cn",
    "https://your-production.com"   # 生产域名
]
# 配置可跨域访问的 域名/IP
CSRF_TRUSTED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",        # 前端开发地址
    "http://127.0.0.1:8000",       # 本地开发地址
    "http://localhost:8000",       # 本地开发地址
    # "https://deepseek.hdu.edu.cn",
    "https://your-production.com"   # 生产域名
]
# 设置 CSRF Cookie 的 SameSite 属性
CSRF_COOKIE_SAMESITE = 'Lax'  # 或 'None' (需要 HTTPS)
SESSION_COOKIE_SAMESITE = 'Lax'

CORS_COOKIE_HTTPONLY = False # 允许前端访问cookie

#跨域增加忽略
CORS_ALLOW_CREDENTIALS = True  # 允许携带Cookie
CORS_ORIGIN_ALLOW_ALL = True
# CORS_ORIGIN_WHITELIST = (
#     '*'
# )

CORS_ALLOW_METHODS = (
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
    'VIEW',
)

CORS_ALLOW_HEADERS = (
    'x-custom-header',
    'XMLHttpRequest',
    'X_FILENAME',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
    'Pragma',
)

# settings.py 添加Channels配置

# ASGI_APPLICATION = 'polls.routing.application'
ASGI_APPLICATION = 'mysite.asgi.application'

 # 生产环境中使用redis做后台，安装redis和channels_redis
 # pip install channels_redis pip install redis
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [("127.0.0.1", 6379)],
        },
    },
}

#  # 设置通道层的通信后台 - 本地测试用
#  CHANNEL_LAYERS = {
#      "default": {
#          "BACKEND": "channels.layers.InMemoryChannelLayer"
#      }
#  }

# daphne -p 8000 mysite.asgi:application

# Add for vuejs

STATIC_URL = '/static/'

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "frontend", "dist", "static"),
]

STATIC_ROOT = BASE_DIR / "staticfiles"  # 收集静态文件的目标目录

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"console": {"class": "logging.StreamHandler"}},
    "loggers": {
        "django.request": {
            "handlers": ["console"],
            "level": "DEBUG",
            "propagate": True,
        }
    },
}
