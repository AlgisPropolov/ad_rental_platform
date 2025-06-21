import os
from pathlib import Path

# 📌 Базовая директория проекта
BASE_DIR = Path(__file__).resolve().parent.parent

# 🛡️ Безопасный режим для локальной разработки
DEBUG = True

# 🌐 Разрешённые хосты
ALLOWED_HOSTS = ["127.0.0.1", "localhost"]

# 🧩 Установленные приложения
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'core',  # наше основное приложение
]

# ⚙️ Middleware
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# 🔁 Основной файл маршрутов
ROOT_URLCONF = 'config.urls'

# 🎨 Настройка шаблонов
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'core' / 'templates'],
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

# 🚀 WSGI-приложение
WSGI_APPLICATION = 'config.wsgi.application'

# 🗄️ База данных (SQLite для разработки)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# 🛑 Проверка паролей (можно упростить в DEV)
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
]

# 🌐 Локализация
LANGUAGE_CODE = 'ru-ru'
TIME_ZONE = 'Europe/Moscow'
USE_I18N = True
USE_TZ = True

# 📁 Путь к статическим файлам
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / "static"]

# 📁 Путь к медиафайлам
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / "media"

# 🧂 Ключ безопасности (не показывать в проде!)
SECRET_KEY = 'django-insecure-замени-на-свой-настоящий-ключ'

# ✅ Значения по умолчанию для primary key
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
