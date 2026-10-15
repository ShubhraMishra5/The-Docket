"""
Settings for The Docket.

All secrets/config that differ between your machine and Render come from
environment variables — see .env.example for the full list.
"""
import os
from pathlib import Path

import dj_database_url
from dotenv import load_dotenv
from django.core.exceptions import ImproperlyConfigured

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

DEBUG = os.environ.get("DJANGO_DEBUG", "True") == "True"

_secret_key = os.environ.get("DJANGO_SECRET_KEY", "")
if not DEBUG and not _secret_key:
    raise ImproperlyConfigured("DJANGO_SECRET_KEY must be set when DJANGO_DEBUG is False.")
SECRET_KEY = _secret_key or "dev-only-insecure-key-change-me"

ALLOWED_HOSTS = os.environ.get("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")

CSRF_TRUSTED_ORIGINS = [
    o for o in os.environ.get("DJANGO_CSRF_TRUSTED_ORIGINS", "").split(",") if o
]

INSTALLED_APPS = [
    # Local apps
    "home",
    "articles",
    "subscribers",
    # Wagtail
    "wagtail.contrib.forms",
    "wagtail.contrib.redirects",
    "wagtail.embeds",
    "wagtail.sites",
    "wagtail.users",
    "wagtail.snippets",
    "wagtail.documents",
    "wagtail.images",
    "wagtail.search",
    "wagtail.admin",
    "wagtail",
    "modelcluster",
    "taggit",
    # Django
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "wagtail.contrib.redirects.middleware.RedirectMiddleware",
]

ROOT_URLCONF = "docket.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "home.context_processors.nav_sections",
            ],
        },
    },
]

WSGI_APPLICATION = "docket.wsgi.application"

# Database. Defaults to local SQLite; set DATABASE_URL on Render to use Postgres.
DATABASES = {
    "default": dj_database_url.config(
        default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
        conn_max_age=0,
        conn_health_checks=True,
    )
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "Asia/Kolkata"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"},
}
MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
if not DEBUG:
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_SSL_REDIRECT = True

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# --- Wagtail ---
WAGTAIL_SITE_NAME = "The Docket"
WAGTAILSEARCH_BACKENDS = {
    "default": {
        "BACKEND": "wagtail.search.backends.database",
    }
}
WAGTAILADMIN_BASE_URL = os.environ.get("WAGTAILADMIN_BASE_URL", "http://localhost:8000")
WAGTAIL_ALLOW_UNICODE_SLUGS = False

# --- Rich text: which formatting controls are available to editors ---
# Custom underline, alignment, and font styles are registered in
# articles/wagtail_hooks.py.
WAGTAILADMIN_RICH_TEXT_EDITORS = {
    "default": {
        "WIDGET": "wagtail.admin.rich_text.DraftailRichTextArea",
        "OPTIONS": {
            "features": [
                "bold", "italic", "underline", "ol", "ul", "link",
                "align-left", "align-center", "align-right",
                "font-times", "font-sitka", "font-garamond",
            ]
        },
    }
}

# --- Mailchimp (subscriber list + monthly draft campaign) ---
MAILCHIMP_API_KEY = os.environ.get("MAILCHIMP_API_KEY", "")
MAILCHIMP_AUDIENCE_ID = os.environ.get("MAILCHIMP_AUDIENCE_ID", "")
MAILCHIMP_REPLY_TO = os.environ.get("MAILCHIMP_REPLY_TO", "thedocketrepository@outlook.com")
OWNER_NOTIFICATION_EMAIL = os.environ.get(
    "OWNER_NOTIFICATION_EMAIL", "thedocketrepository@outlook.com"
)
PUBLIC_BASE_URL = os.environ.get("PUBLIC_BASE_URL", "")

# --- Email for the thank-you and owner notification (plain SMTP) ---
EMAIL_HOST = os.environ.get("EMAIL_HOST", "")
EMAIL_PORT = int(os.environ.get("EMAIL_PORT", "587"))
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD", "")
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = os.environ.get(
    "DEFAULT_FROM_EMAIL", EMAIL_HOST_USER or "noreply@localhost"
)
EMAIL_BACKEND = (
    "django.core.mail.backends.smtp.EmailBackend"
    if EMAIL_HOST else "django.core.mail.backends.console.EmailBackend"
)

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"console": {"class": "logging.StreamHandler"}},
    "root": {"handlers": ["console"], "level": "INFO"},
}
