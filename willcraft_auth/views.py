import calendar
import json
from urllib import parse

from django.contrib.auth import login as django_login
from django.contrib.auth import logout as django_logout
from django.contrib.auth.models import update_last_login
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.debug import sensitive_post_parameters
from oauth2_provider.exceptions import OAuthToolkitError
from oauth2_provider.models import get_access_token_model, get_grant_model
from oauth2_provider.scopes import get_scopes_backend
from oauth2_provider.settings import oauth2_settings
from oauth2_provider.signals import app_authorized
from oauth2_provider.views.base import TokenView
from oauth2_provider.views.mixins import OAuthLibMixin
from rest_auth.views import PasswordResetConfirmView, PasswordResetView
from rest_framework import generics, status
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from partners.models import Partners
from services.email.email_utils import SendEmailHelper
from utils.views import CustomGetCreateUpdateView

from .models import *
from .oauth2_validators import CustomOAuth2Validator
from .serializers import *

sensitive_post_parameters_m = method_decorator(
    sensitive_post_parameters(
        "password", "old_password", "new_password1", "new_password2", "repeat_password"
    )
)


class UserDetailsView(CustomGetCreateUpdateView):
    """
    Reads and updates UserModel fields
    Accepts GET, PUT, PATCH methods.
    Default accepted fields: username, first_name, last_name
    Default display fields: pk, username, email, first_name, last_name
    Read-only fields: pk, email
    Returns UserModel fields.
    """

    serializer_class = WillCraftUserPersonalDetailsSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return self.request.user.personal_details


class GetTokenMixin(OAuthLibMixin):
    def get_params_from_url(self):
        path = self.request.build_absolute_uri()
        urldata = dict(parse.parse_qsl(parse.urlsplit(path).query))
        data = z = {**self.request.data, **urldata}
        return data

    def get_token_response(self, request):
        url, headers, body, status = self.create_token_response(request)
        if status == 200:
            access_token = json.loads(body).get("access_token")
            if access_token is not None:
                token = get_access_token_model().objects.get(token=access_token)
                app_authorized.send(sender=self, request=request, token=token)

        response = HttpResponse(content=body, status=status)

        for k, v in headers.items():
            response[k] = v
        return response

    def get_token_redirect_response(self, request):  # pragma: no cover
        # for use if partners use server side rendering to push users to success url
        response = self.get_token_response(request)
        response["location"] = "http://127.0.0.1:8000/success/"
        return response

    def get_authorization_response(
        self, request, scopes, credentials, application
    ):  # pragma: no cover
        uri, headers, body, status = self.create_authorization_response(
            request=request,
            scopes=" ".join(scopes),
            credentials=credentials,
            allow=True,
        )

        # deconstructing the uri to find the authorization code and returning that
        authorization_code = uri.split("?code=")[1]
        redirect_url = uri.split("?code=")[0]
        return Response(
            {
                "skip_auth": application.skip_authorization,
                "code": authorization_code,
                "redirect_url": redirect_url,
            },
            status=status,
        )


class LoginView(GetTokenMixin, GenericAPIView):
    """
    Check the credentials and return an Access Token
    if the credentials are valid and authenticated.

    Calls Django Auth login method to register User ID
    in Django session framework

    Accept the following POST parameters: email, password
    Returns an Access Token.

    Also put grant_type and client_id in url params
    """

    permission_classes = (AllowAny,)
    serializer_class = LoginSerializer

    server_class = oauth2_settings.OAUTH2_SERVER_CLASS
    validator_class = CustomOAuth2Validator
    oauthlib_backend_class = oauth2_settings.OAUTH2_BACKEND_CLASS

    @sensitive_post_parameters_m
    def dispatch(self, *args, **kwargs):
        return super(LoginView, self).dispatch(*args, **kwargs)

    def login(self):
        django_login(self.request, self.user)
        update_last_login(None, self.user)

    def post(self, request, *args, **kwargs):
        self.request = request
        self.serializer = self.get_serializer(
            data=self.request.data, context={"request": request}
        )
        self.serializer.is_valid(raise_exception=True)
        self.user = self.serializer.validated_data["user"]
        self.login()

        # Add user to partner
        partner_client_id = request.data.get("partner_client_id", None)
        if partner_client_id:
            self.user.add_user_to_partner(client_id=partner_client_id)

        return self.get_token_response(request)


class CustomPasswordResetView(PasswordResetView):
    """
    Calls Django Auth PasswordResetForm save method.
    Accepts the following POST parameters: email
    Returns the success/fail message.
    """

    serializer_class = CustomPasswordResetSerializer


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    """
    Password reset e-mail link is confirmed, therefore
    this resets the user's password.
    Accepts the following POST parameters: token, uid,
        new_password1, new_password2
    Returns the success/fail message.
    """

    serializer_class = CustomPasswordResetConfirmSerializer


class TokenLoginView(GetTokenMixin, GenericAPIView):
    """
    Login with email that is register with token_register also and returns Access Token

    Accept the following POST parameters: email, password, repeat_password, grant_type, client_id
    Returns an Access Token.
    """

    permission_classes = (AllowAny,)
    serializer_class = TokenLoginSerializer

    server_class = oauth2_settings.OAUTH2_SERVER_CLASS
    validator_class = CustomOAuth2Validator
    oauthlib_backend_class = oauth2_settings.OAUTH2_BACKEND_CLASS

    @sensitive_post_parameters_m
    def dispatch(self, *args, **kwargs):
        return super(TokenLoginView, self).dispatch(*args, **kwargs)

    def login(self):
        django_login(self.request, self.user)
        update_last_login(None, self.user)

    def post(self, request, *args, **kwargs):
        self.request = request
        self.serializer = self.get_serializer(
            data=request.data, context={"request": request}
        )
        self.serializer.is_valid(raise_exception=True)
        self.serializer.save(self.request)
        self.user = self.serializer.validated_data["user"]
        self.login()

        # Add user to partner
        partner_client_id = request.data.get("partner_client_id", None)
        if partner_client_id:
            self.user.add_user_to_partner(client_id=partner_client_id)

        return self.get_token_response(request)


class LogoutView(APIView):
    """
    Calls Django logout method and delete the Token object
    assigned to the current User object.
    Accepts/Returns nothing.
    """

    permission_classes = (AllowAny,)

    def get(self, request, *args, **kwargs):  # pragma: no cover
        if getattr(settings, "ACCOUNT_LOGOUT_ON_GET", False):
            response = self.logout(request)
        else:
            response = self.http_method_not_allowed(request, *args, **kwargs)

        return self.finalize_response(request, response, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.logout(request)

    def logout(self, request):
        try:
            request.user.auth_token.delete()
        except (AttributeError, ObjectDoesNotExist):
            pass
        if getattr(settings, "REST_SESSION_LOGIN", True):
            django_logout(request)

        response = Response(
            {"detail": _("Successfully logged out.")}, status=status.HTTP_200_OK
        )
        if getattr(settings, "REST_USE_JWT", False):  # pragma: no cover
            from rest_framework_jwt.settings import api_settings as jwt_settings

            if jwt_settings.JWT_AUTH_COOKIE:
                response.delete_cookie(jwt_settings.JWT_AUTH_COOKIE)
        return response


class RegisterView(GetTokenMixin, generics.CreateAPIView):
    """
    Take credentials and registers user then return an Access Token.

    Accept the following POST parameters: email, password, repeat_password
    Returns an Access Token.

    Also put grant_type and client_id in url params
    """

    serializer_class = RegisterSerializer
    permission_classes = (AllowAny,)

    server_class = oauth2_settings.OAUTH2_SERVER_CLASS
    validator_class = CustomOAuth2Validator
    oauthlib_backend_class = oauth2_settings.OAUTH2_BACKEND_CLASS

    @sensitive_post_parameters_m
    def dispatch(self, *args, **kwargs):
        return super(RegisterView, self).dispatch(*args, **kwargs)

    def create(self, request, *args, **kwargs):
        partner_client_id = request.data.get("partner_client_id", None)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # Doing an atomic transaction to make sure that changes are rolled back in case of an error
        with transaction.atomic():
            user = self.perform_create(serializer)
            if partner_client_id:
                user.add_user_to_partner(client_id=partner_client_id)
            response = self.get_token_response(request)
        return response

    def perform_create(self, serializer):
        user = serializer.save(self.request)

        # complete_signup(self.request._request, user,
        #                 allauth_settings.EMAIL_VERIFICATION, None)
        return user


class TokenRegisterView(RegisterView):
    """
    Take only email and registers user then return an Access Token.

    Accept the following POST parameters: email, client_id, password
    Returns an Access Token.
    """

    serializer_class = TokenRegisterSerializer

    def create(self, request, *args, **kwargs):
        partner_client_id = request.data.get("partner_client_id", None)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # Doing an atomic transaction to make sure that changes are rolled back in case of an error
        with transaction.atomic():
            user = self.perform_create(serializer)
            # adding user to users that the partners have referred to apply discounts
            if partner_client_id:
                user.add_user_to_partner(client_id=partner_client_id)
            response = self.get_token_response(request)

            token = json.loads(response.content)['access_token']
            email = self.request.data["email"]
            current_site = self.request.data.get("domain", "willcraftnow.com")
            token_link = f"https://{current_site}/en/auth/token/?email={email}&token={token}"

            SendEmailHelper(user=user).send_token_email(email, token_link)

        return response


class IfEmailIsRegisteredView(generics.GenericAPIView):
    """Checks to see if the email has an associated user, and returns a 200
    response if true - otherwise returns a 403

    endpoint: /auth/is_user/

    get: Return a 200/403 response based on whether the email is associated to a user
    """

    permission_classes = (AllowAny,)
    queryset = None
    serializer_class = IfEmailIsRegisteredSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data)


class GetClientNameView(GenericAPIView, GetTokenMixin):
    """
    To get client id detail returns client name
    provide client id in as url params in get call
    """

    permission_classes = (AllowAny,)

    def get(self, request, *args, **kwargs):
        data = self.get_params_from_url()
        if "client_id" in data:
            try:
                application = get_application_model().objects.get(
                    client_id=data["client_id"]
                )
            except:
                return Response(
                    {"client_name": "Application Does Not Exist!"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            return Response(
                {"client_name": application.name}, status=status.HTTP_200_OK
            )
        elif "client_name" in data:
            try:
                application = get_application_model().objects.get(
                    name__iexact=data["client_name"]
                )
            except:
                return Response(
                    {"client_id": "Application Does Not Exist!"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            return Response(
                {"client_id": application.client_id}, status=status.HTTP_200_OK
            )
        else:
            return Response(
                {"client_id or client_name param required."},
                status=status.HTTP_403_FORBIDDEN,
            )


class AuthorizationView(GenericAPIView, GetTokenMixin):  # pragma: no cover
    permission_classes = (AllowAny,)
    serializer_class = AuthorizationSerializer

    server_class = oauth2_settings.OAUTH2_SERVER_CLASS
    validator_class = CustomOAuth2Validator
    oauthlib_backend_class = oauth2_settings.OAUTH2_BACKEND_CLASS

    def post(self, request, *args, **kwargs):
        self.serializer = self.get_serializer(
            data=request.data, context={"request": request}
        )
        self.serializer.is_valid(raise_exception=True)
        data = self.serializer.validated_data
        credentials = {
            "client_id": data["client_id"],
            "redirect_uri": None,
            "response_type": None,
            "state": None,
        }
        application = get_application_model().objects.get(
            client_id=data["client_id"]
        )

        try:
            scopes, credentials = self.validate_authorization_request(request)
        except OAuthToolkitError as error:
            error_json = json.loads(error.oauthlib_error.json)
            status_code = error.oauthlib_error.status_code
            return Response(error_json, status=status_code)

        request.user = get_user_model().objects.get(email=data["email"])

        # need to change this dictionary if want to have custom scope
        all_scopes = get_scopes_backend().get_all_scopes()

        if "allow" in request.data and request.data["allow"]:
            request.user.add_user_to_partner(application=application)
            return self.get_authorization_response(
                request, all_scopes, credentials, application
            )

        tokens = (
            get_grant_model()
            .objects.filter(user=request.user, application=application,)
            .all()
        )

        # check past authorizations regarded the same scopes as the current one, if so grant access
        # TODO check previous token scope against the current requested scope.
        if tokens:
            return self.get_authorization_response(
                request, scopes, credentials, application
            )

        # if skip auth, grant access
        if application.skip_authorization:
            request.user.add_user_to_partner(application=application)
            return self.get_authorization_response(
                request, scopes, credentials, application
            )
        else:
            return Response(
                {"skip_auth": application.skip_authorization, },
                status=status.HTTP_200_OK,
            )


class IntrospectTokenView(GenericAPIView):
    """
    Implements an endpoint for token introspection based
    on RFC 7662 https://tools.ietf.org/html/rfc7662

    This view is used as opposed to the provided one because
    the original view rquired that the request must pass a OAuth2 Bearer Token
    which is allowed to access the scope `introspection`. This view just
    requires any token.
    """

    permission_classes = (AllowAny,)
    required_scopes = []

    @staticmethod
    def get_token_response(token_value=None):
        try:
            token = get_access_token_model().objects.get(token=token_value)
        except ObjectDoesNotExist:
            return HttpResponse(
                content=json.dumps({"active": False}),
                status=status.HTTP_401_UNAUTHORIZED,
                content_type="application/json",
            )
        else:
            if not token.is_expired():
                data = {
                    "active": True,
                    "scope": token.scope,
                    "exp": int(calendar.timegm(token.expires.timetuple())),
                }
                if token.application:
                    data["client_id"] = token.application.client_id
                if token.user:
                    data["email"] = token.user.email
                    user_type = ["USER"]
                    if token.user.is_lawyer:
                        user_type.append("LAWYER")
                    if token.user.is_superuser or token.user.is_staff:
                        user_type.append("ADMIN")
                    if Partners.objects.filter(agents__in=[token.user]).exists():
                        user_type.append("PARTNER")
                    data["user_type"] = user_type
                return HttpResponse(
                    content=json.dumps(data),
                    status=200,
                    content_type="application/json",
                )
            else:
                return HttpResponse(
                    content=json.dumps({"active": False, }),
                    status=200,
                    content_type="application/json",
                )

    def get(self, request, *args, **kwargs):
        """
        Get the token from the URL parameters.
        URL: https://example.com/introspect?token=mF_9.B5f-4.1JqM

        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        return self.get_token_response(request.GET.get("token", None))


class GetClientId(APIView):
    """
    Get an client id in return on get call
    """

    permission_classes = (AllowAny,)

    def get(self, request):
        application = get_application_model().objects.get(name="WillCraft")
        return Response({"client_id": application.client_id})


class ResendTokenEmail(APIView):
    """A Custom APIView resends the email to the user for token login

    endpoint: /auth/resend_token_email/

    post: Takes a token in the request body and migrates
            all orders belonging to that token to the user
    """

    permission_classes = (AllowAny,)

    def post(self, request):
        """Transfers all of the token's (from request.body)
        orders to the logged in user
        """
        email = self.request.data["email"]
        user = get_user_model().objects.get(email=email)
        token = get_access_token_model().objects.filter(
            user=user).latest('id')
        current_site = self.request.data.get("domain", "willcraftnow.com")
        token_link = f"https://{current_site}/en/auth/token/?email={email}&token={token}"

        if user:
            SendEmailHelper(user=user).send_token_email(
                email, token_link)

            return Response({"message": "Email Sent."})
        else:
            return Response({"User not found."}, status=status.HTTP_400_BAD_REQUEST)


class TokenView(TokenView):
    """
    Implements an endpoint to provide access tokens

    The endpoint is used in the following flows:
    * Authorization code
    * Password
    * Client credentials
    """

    validator_class = CustomOAuth2Validator
