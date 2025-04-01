# Mine - Django Chat Application

A real-time chat application built with Django, Django Channels, and Tailwind CSS.

## Setup Guide

### Prerequisites
- Python 3.8+
- Django 5.1

### Installation Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/mine.git
   cd mine
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   # Core packages
   pip install django daphne channels
   pip install django-allauth django-allauth-ui
   pip install django-widget-tweaks slippers
   pip install djangorestframework
   pip install django-tailwind
   ```

4. **Configure settings.py**

   - Generate a secret key:
     ```python
     # Run this in a Python console
     from django.core.management.utils import get_random_secret_key
     print(get_random_secret_key())
     ```
   
   - Add the generated key to `SECRET_KEY` in settings.py
   
   - Set up Google OAuth credentials in `SOCIALACCOUNT_PROVIDERS`
   
   - Configure email settings:
     ```python
     EMAIL_HOST_USER = 'your-email@gmail.com'
     EMAIL_HOST_PASSWORD = 'your-app-password'
     ```

5. **Set up database**
   ```bash
   python manage.py migrate
   ```

6. **Create a superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Set up Tailwind CSS**
   ```bash
   python manage.py tailwind install
   python manage.py tailwind build
   ```

8. **Run the development server**
   ```bash
   python manage.py runserver
   ```

   Access the application at http://127.0.0.1:8000/

## Project Configuration Details

### Installed Apps
```python
INSTALLED_APPS = [
    "daphne",
    'channels',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'chatss',
    "allauth_ui",
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    "widget_tweaks",
    "slippers",
    'tailwind',
    'theme',
]
```

### Authentication Settings
```python
AUTH_USER_MODEL = 'chatss.accUser'

ACCOUNT_USER_MODEL_USERNAME_FIELD = 'username'
ACCOUNT_SIGNUP_PASSWORD_VERIFICATION = True
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = True
ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_EMAIL_VERIFICATION = 'mandatory'
ACCOUNT_EMAIL_CONFIRMATION_ANONYMOUS_REDIRECT_URL = '/accounts/login/'

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

ACCOUNT_FORMS = {
    'signup': 'chatss.forms.CustomSignupForm',
}

LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/accounts/login/'

ALLAUTH_UI_THEME = "halloween"
```

### Channels Configuration
```python
ASGI_APPLICATION = 'mine.asgi.application'
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer',
    },
}
```

### REST Framework
```python
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly'
    ]
}
```

### Static and Media Files
```python
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'static'
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"
```

### Tailwind CSS
```python
TAILWIND_APP_NAME = 'theme'
```

## Directory Structure

Make sure your project directory includes:

- `mine/` - Project directory
  - `middleware.py` - Contains `UpdateLastOnlineMiddleware`
  - `asgi.py`, `wsgi.py`, `urls.py`, etc.
- `chatss/` - Main application
  - `forms.py` - Contains `CustomSignupForm`
  - Models including custom user model `accUser`
- `templates/` - HTML templates
- `theme/` - Tailwind CSS app

## Production Considerations

For production deployment:

1. Set `DEBUG = False`
2. Configure `ALLOWED_HOSTS` with your domain
3. Use a production database (PostgreSQL recommended)
4. Consider using Redis for channels:
   ```python
   CHANNEL_LAYERS = {
       'default': {
           'BACKEND': 'channels_redis.core.RedisChannelLayer',
           'CONFIG': {
               "hosts": [('127.0.0.1', 6379)],
           },
       },
   }
   ```
5. Enable security settings:
   ```python
   SESSION_COOKIE_SECURE = True
   CSRF_COOKIE_SECURE = True
   SECURE_SSL_REDIRECT = True
   ```
