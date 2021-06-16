import os
from .base import BASE_DIR

# Internationalization
# https://docs.djangoproject.com/en/2.0/topics/i18n/

LANGUAGE_CODE = "en"

LANGUAGES = (("en", "English"), ("zh-cn", "Chinese"))

TIME_ZONE = "Asia/Singapore"

USE_I18N = True

LOCALE_PATHS = (os.path.join(BASE_DIR, "locale"),)

USE_L10N = True

USE_TZ = True
