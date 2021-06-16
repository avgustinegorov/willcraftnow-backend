from allauth.account.adapter import get_adapter
from allauth.account.utils import setup_user_email
from allauth.utils import email_address_exists
from django.conf import settings
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth.tokens import default_token_generator
from django.utils.translation import ugettext_lazy as _
from oauth2_provider.models import (get_access_token_model,
                                    get_application_model)
from rest_auth.serializers import (PasswordResetConfirmSerializer,
                                   PasswordResetSerializer)
from rest_framework import exceptions, serializers

from partners.models import ApplicationStore, Partners
from persons.models import Person
from persons.serializers import PersonSerializer
from utils.serializers import CustomModelSerializer
from utils.fields import CharField, EmailField
# Get the UserModel
UserModel = get_user_model()


class IfEmailIsRegisteredSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True, label=_("Email"))
    status = serializers.SerializerMethodField(
        read_only=True, required=False, label=_("Status")
    )

    def get_status(self, instance):
        try:
            user = UserModel.objects.get(email=instance["email"])
        except:
            return "Not Registered"

        if user and user.has_usable_password():
            return "Registered"
        elif user and not user.has_usable_password():
            return "Token"


class WillCraftUserPersonalDetailsSerializer(PersonSerializer):
    """A custom serializer for our user model
    which overwrites the provided detail serializer by
    Django-Rest-Auth by adding support for personal details
    """

    user_type = serializers.SerializerMethodField(
        read_only=True, required=False)
    referring_applications = serializers.SerializerMethodField(
        read_only=True, required=False
    )

    def create(self, validated_data):
        """ Sets the request's user on the Order if it's present """
        # Is this really required? If no, delete.
        request = self.context.get("request", None)
        user = request.user
        personal_details = super().create(
            validated_data) if not user.personal_details else super().update(user.personal_details, validated_data)
        user.personal_details = personal_details
        user.save()
        return personal_details

    def get_user_type(self, instance):
        return instance.user_detail.get_user_type

    def get_referring_applications(self, instance):
        application_stores = ApplicationStore.objects.filter(
            referred_users__in=[instance.user_detail])
        return [application_store.application.name for application_store in application_stores]

    class Meta:
        model = Person
        fields = [
            "id",
            "name",
            "id_number",
            "id_document",
            "country_of_issue",
            "date_of_birth",
            "address",
            "block_only_address",
            "real_estate_type",
            "block_number",
            "floor_number",
            "unit_number",
            "street_name",
            "country",
            "postal_code",
            "religion",
            "citizenship_status",
            "relationship_status",
            "underage_children",
            "gender",
            "relationship",
            "relationship_other",
            "contact_number",
            "email",
            "display_name",
            "is_private_housing",
            "referring_applications",
            "user_type",
            'entity_type'
        ]


class WillCraftUserSerializer(CustomModelSerializer):
    """A custom serializer for our user model
    which overwrites the provided detail serializer by
    Django-Rest-Auth by adding support for personal details
    """

    personal_details = PersonSerializer(required=False)
    will_status = serializers.SerializerMethodField(
        read_only=True, required=False)

    class Meta:
        model = UserModel
        fields = (
            "pk",
            "username",
            "email",
            "first_name",
            "last_name",
            "personal_details",
            "will_status",
        )
        read_only_fields = ("email",)


class LoginSerializer(serializers.Serializer):
    email = EmailField(
        display=False, required=True, label=_("Email"))
    password = serializers.CharField(
        label=_("Password"), style={"input_type": "password"}
    )

    def authenticate(self, **kwargs):
        return authenticate(self.context["request"], **kwargs)

    def validate_email(self, email):
        email = get_adapter().clean_email(email)
        if email and not email_address_exists(email):
            raise serializers.ValidationError(_("Email is not registered."))
        return email

    def _validate_email(self, email, password):
        user = None

        if email and password:
            user = self.authenticate(email=email, password=password)
        else:
            msg = _('Must include "email" and "password".')
            raise exceptions.ValidationError(msg)

        return user

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        user = self._validate_email(email, password)

        # Did we get back an active user?
        if user:
            if not user.is_active:
                msg = _("User account is disabled.")
                raise exceptions.ValidationError(msg)
        else:
            msg = _("Unable to log in with provided credentials.")
            raise exceptions.ValidationError(msg)

        # If required, is the email verified?
        # uncomment if verification of email is required
        # email_address = user.emailaddress_set.get(email=user.email)
        # if not email_address.verified:
        #     raise serializers.ValidationError(
        #         _('E-mail is not verified.'))

        attrs["user"] = user
        return attrs


class TokenLoginSerializer(LoginSerializer):
    password = serializers.CharField(
        label=_("Password"), style={"input_type": "password"}, required=True
    )
    repeat_password = serializers.CharField(
        required=True, label=_("Password (Again)"), style={"input_type": "password"},
    )
    token = CharField(
        label=_("Token"), required=True, display=False
    )

    def validate_email(self, email):
        email = get_adapter().clean_email(email)
        if email and not email_address_exists(email):
            raise serializers.ValidationError(_("Email does not exist."))
        return email

    def validate_password(self, password):
        return get_adapter().clean_password(password)

    def validate_repeat_password(self, password):
        return get_adapter().clean_password(password)

    def validate(self, data):
        email = data.get("email")
        email = get_adapter().clean_email(email)
        token = data.get("token")

        if email:
            user = UserModel.objects.get(email=email)
        else:
            msg = _('Must include "email".')
            raise exceptions.ValidationError(msg)

        if data["password"] != data["repeat_password"]:
            raise serializers.ValidationError(
                _("The two password fields didn't match.")
            )

        # Did we get back an active user?
        if user:
            if not get_access_token_model().objects.filter(user=user, token=token).exists():
                msg = _("Token Error. Please Contact Us Directly.")
                raise exceptions.ValidationError(msg)
            if not user.is_active:
                msg = _("User account is disabled.")
                raise exceptions.ValidationError(msg)
            if user.has_usable_password():
                msg = _("Password exists, token login not authorised.")
                raise exceptions.ValidationError({"password": msg})
        else:
            msg = _("Unable to log in with provided credentials.")
            raise exceptions.ValidationError(msg)
        data["user"] = user
        return data

    def get_cleaned_data(self):
        return {
            "user": self.validated_data.get("user", ""),
            "password": self.validated_data.get("password", ""),
        }

    def save(self, request):
        self.cleaned_data = self.get_cleaned_data()
        user = self.cleaned_data["user"]
        user.set_password(self.cleaned_data["password"])
        user.save()
        return user


class PartnerRegisterSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True, label=_("Email"))

    def validate_email(self, email):
        email = get_adapter().clean_email(email)
        if email and email_address_exists(email):
            raise serializers.ValidationError(
                _("A user is already registered with this e-mail address.")
            )
        return email

    def get_cleaned_data(self):
        return {"email": self.validated_data.get("email", "")}

    def save(self, request):
        """Creates and sets the user's personal details
        1-1 field if the personal_details field is provided
        in the request data before saving the actual user
        """
        adapter = get_adapter()
        user = adapter.new_user(request)

        self.cleaned_data = self.get_cleaned_data()

        adapter.save_user(request, user, self)
        setup_user_email(request, user, [])
        return user


class RegisterSerializer(serializers.Serializer):
    """Custom serializer for overriding the provided registration
    serializer from django-rest-auth
    """

    email = EmailField(
        display=False, required=True, label=_("Email"))
    password = serializers.CharField(label=_("Password"))
    repeat_password = serializers.CharField(label=_("Password (Again)"))

    def validate_email(self, email):
        email = get_adapter().clean_email(email)
        if email and email_address_exists(email):
            raise serializers.ValidationError(
                _("A user is already registered with this e-mail address.")
            )
        return email

    def validate_password(self, password):
        return get_adapter().clean_password(password)

    def validate_repeat_password(self, repeat_password):
        return get_adapter().clean_password(repeat_password)

    def validate(self, data):
        if data["password"] != data["repeat_password"]:
            raise serializers.ValidationError(
                _("The two password fields didn't match.")
            )
        return data

    def get_cleaned_data(self):
        return {
            "password": self.validated_data.get("password", ""),
            "email": self.validated_data.get("email", ""),
        }

    def save(self, request):
        """Creates and sets the user's personal details
        1-1 field if the personal_details field is provided
        in the request data before saving the actual user
        """
        adapter = get_adapter()
        user = adapter.new_user(request)

        self.cleaned_data = self.get_cleaned_data()

        adapter.save_user(request, user, self)
        setup_user_email(request, user, [])
        return user


class TokenRegisterSerializer(RegisterSerializer):
    password = None
    repeat_password = None

    def validate_password(self, password):
        pass

    def validate_repeat_password(self, repeat_password):
        pass

    def validate(self, data):
        return data

    def get_cleaned_data(self):
        return {"email": self.validated_data.get("email", "")}


class CustomPasswordResetSerializer(PasswordResetSerializer):
    """
    Serializer for requesting a password reset e-mail.
    """

    def save(self):
        request = self.context.get("request")
        # Set some values to trigger the send_email method.
        opts = {
            "domain_override": None,
            "token_generator": default_token_generator,
            "request": None,
            "html_email_template_name": "email_templates/password_reset_email.html",
            "subject_template_name": "email_templates/password_reset_subject.txt",
            "email_template_name": "email_templates/password_reset_email.txt",
            "extra_email_context": None,
            "use_https": request.is_secure(),
            "from_email": getattr(settings, "EMAIL_MAIN"),
            "request": request,
        }

        opts.update(self.get_email_options())
        self.reset_form.save(**opts)


class CustomPasswordResetConfirmSerializer(PasswordResetConfirmSerializer):
    """
    Serializer for requesting a password reset e-mail.
    """

    new_password1 = serializers.CharField(
        max_length=128, label=_("New Password"))
    new_password2 = serializers.CharField(
        max_length=128, label=_("New Password (Again)")
    )


class PasswordChangeSerializer(serializers.Serializer):  # pragma: no cover
    old_password = serializers.CharField(max_length=128)
    new_password1 = serializers.CharField(max_length=128)
    new_password2 = serializers.CharField(max_length=128)

    set_password_form_class = SetPasswordForm

    def __init__(self, *args, **kwargs):
        self.old_password_field_enabled = getattr(
            settings, "OLD_PASSWORD_FIELD_ENABLED", False
        )
        self.logout_on_password_change = getattr(
            settings, "LOGOUT_ON_PASSWORD_CHANGE", False
        )
        super(PasswordChangeSerializer, self).__init__(*args, **kwargs)

        if not self.old_password_field_enabled:
            self.fields.pop("old_password")

        self.request = self.context.get("request")
        self.user = getattr(self.request, "user", None)

    def validate_old_password(self, value):
        invalid_password_conditions = (
            self.old_password_field_enabled,
            self.user,
            not self.user.check_password(value),
        )

        if all(invalid_password_conditions):
            err_msg = _(
                "Your old password was entered incorrectly. Please enter it again."
            )
            raise serializers.ValidationError(err_msg)
        return value

    def validate(self, attrs):
        self.set_password_form = self.set_password_form_class(
            user=self.user, data=attrs
        )

        if not self.set_password_form.is_valid():
            raise serializers.ValidationError(self.set_password_form.errors)
        return attrs

    def save(self):
        self.set_password_form.save()
        if not self.logout_on_password_change:
            from django.contrib.auth import update_session_auth_hash

            update_session_auth_hash(self.request, self.user)


class AuthorizationSerializer(serializers.Serializer):
    """
    http://127.0.0.1:8000/authorize?email=dsssdddd1d2f@gmail.com&client_id=TUWxEkxI5I3LExOEd947utZ5GPJ8ts6HMiepnVwk&redirect_back=true
    """

    allow = serializers.BooleanField(required=False)
    email = CharField(display=False)
    scope = serializers.CharField(required=False, allow_blank=True)
    client_id = serializers.CharField(required=True)
    response_type = serializers.CharField()

    def validate_client_id(self, client_id):  # pragma: no cover
        if not get_application_model().objects.filter(client_id=client_id).exists():
            msg = _("Application Does Not Exist.")
            raise exceptions.ValidationError(msg)
        return client_id

    def validate_email(self, email):  # pragma: no cover
        email = get_adapter().clean_email(email)
        if not email_address_exists(email):
            raise serializers.ValidationError(_("Email does not exist."))
        return email


class SkipAuthorizationSerializer(serializers.Serializer):  # pragma: no cover

    client_id = serializers.CharField(required=True)

    def validate_client_id(self, client_id):
        if not get_application_model().objects.filter(client_id=client_id).exists():
            msg = _("Application Does Not Exist.")
            raise exceptions.ValidationError(msg)
        return client_id


class WillCraftTokenRegistrationSerializer(serializers.Serializer):  # pragma: no cover

    email = CharField(display=False)
    token = CharField(display=False)
    password = CharField(display=False)
    repeat_password = CharField(display=False)

    def validate_password(self, password):
        return get_adapter().clean_password(password)

    def validate(self, data):
        if data["password"] != data["repeat_password"]:
            raise serializers.ValidationError(
                _("The two password fields didn't match.")
            )
        return data

    def validate_token(self, token):
        self.user = WillCraftUser.objects.get(email=data["email"])
        token = Token.objects.get(key=data["token"])
        if token.user != self.user:
            raise serializers.ValidationError(_("Invalid token."))

    def get_cleaned_data(self):
        return {
            "password": self.validated_data.get("password", ""),
        }

    def save(self, request):
        user = self.user
        self.cleaned_data = self.get_cleaned_data()
        user.set_password(self.cleaned_data["password"])
        user.save()
        return user
