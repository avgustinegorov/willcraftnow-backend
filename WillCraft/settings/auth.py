# Password validation
# https://docs.djangoproject.com/en/2.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": (
            "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
        ),
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator", },
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator", },
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator", },
]

# User substitution - Custom User model
# https://docs.djangoproject.com/en/1.11/topics/auth/customizing/#auth-custom-user
AUTH_USER_MODEL = "willcraft_auth.WillCraftUser"

# custom adapter for allauth to comply with the custom user model
ACCOUNT_ADAPTER = "willcraft_auth.adapter.CustomisedAccountAdapter"

REST_AUTH_SERIALIZERS = {
    "USER_DETAILS_SERIALIZER": "willcraft_auth.serializers.WillCraftUserSerializer"
}

REST_AUTH_REGISTER_SERIALIZERS = {
    "REGISTER_SERIALIZER": (
        "willcraft_auth.serializers.WillCraftUserRegistrationSerializer"
    )
}

# needs token auth to for frontend calls, and Session Auth for direct calls
# disable Session Auth in production
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "oauth2_provider.contrib.rest_framework.OAuth2Authentication",
        # 'willcraft_auth.authentication.BearerAuthentication',
        # 'rest_framework.authentication.SessionAuthentication',
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "oauth2_provider.contrib.rest_framework.TokenHasReadWriteScope",
    ),
    'DEFAULT_SCHEMA_CLASS': 'rest_framework.schemas.coreapi.AutoSchema',
    "DEFAULT_METADATA_CLASS": "utils.serializers.CustomMetaData",
}

# Following is added to enable registration with email instead of username
AUTHENTICATION_BACKENDS = (
    # Needed to login by username in Django admin, regardless of `allauth`
    "django.contrib.auth.backends.ModelBackend",
)

OAUTH2_PROVIDER_ACCESS_TOKEN_MODEL = "oauth2_provider.AccessToken"
OAUTH2_PROVIDER_APPLICATION_MODEL = "oauth2_provider.Application"
OAUTH2_PROVIDER_REFRESH_TOKEN_MODEL = "oauth2_provider.RefreshToken"
