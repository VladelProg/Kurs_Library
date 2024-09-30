# acme_project/settings.py

INSTALLED_APPS = [    
    'library.apps.',  # Добавляем эту строчку
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',    
] 

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
