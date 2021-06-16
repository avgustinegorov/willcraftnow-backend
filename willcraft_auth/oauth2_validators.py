from oauth2_provider.oauth2_validators import OAuth2Validator
from django.contrib.auth import authenticate, get_user_model


class CustomOAuth2Validator(OAuth2Validator):

    """A Custom Validator to validate for email instead of username"""

    def get_required_param_list(self, request):
        param_list = ("grant_type", "email", "password")
        user = get_user_model().objects.get(email=request.email)
        if not user.has_usable_password():
            param_list = ("grant_type", "email")
        return param_list

    def _get_token_from_authentication_server(
        self, token, introspection_url, introspection_token, introspection_credentials
    ):  # pragma: no cover
        """Use external introspection endpoint to "crack open" the token.
        :param introspection_url: introspection endpoint URL
        :param introspection_token: Bearer token
        :param introspection_credentials: Basic Auth credentials (id,secret)
        :return: :class:`models.AccessToken`

        Some RFC 7662 implementations (including this one) use a Bearer token while others use Basic
        Auth. Depending on the external AS's implementation, provide either the introspection_token
        or the introspection_credentials.

        If the resulting access_token identifies a email (e.g. Authorization Code grant), add
        that user to the UserModel. Also cache the access_token up until its expiry time or a
        configured maximum time.

        """
        headers = None
        if introspection_token:
            headers = {"Authorization": "Bearer {}".format(introspection_token)}
        elif introspection_credentials:
            client_id = introspection_credentials[0].encode("utf-8")
            client_secret = introspection_credentials[1].encode("utf-8")
            basic_auth = base64.b64encode(client_id + b":" + client_secret)
            headers = {"Authorization": "Basic {}".format(basic_auth.decode("utf-8"))}

        try:
            response = requests.post(
                introspection_url, data={"token": token}, headers=headers
            )
        except requests.exceptions.RequestException:
            log.exception(
                "Introspection: Failed POST to %r in token lookup", introspection_url
            )
            return None

        try:
            content = response.json()
        except ValueError:
            log.exception("Introspection: Failed to parse response as json")
            return None

        if "active" in content and content["active"] is True:
            if "email" in content:
                user, _created = UserModel.objects.get_or_create(
                    **{UserModel.email_FIELD: content["email"]}
                )
            else:
                user = None

            max_caching_time = datetime.now() + timedelta(
                seconds=oauth2_settings.RESOURCE_SERVER_TOKEN_CACHING_SECONDS
            )

            if "exp" in content:
                expires = datetime.utcfromtimestamp(content["exp"])
                if expires > max_caching_time:
                    expires = max_caching_time
            else:
                expires = max_caching_time

            scope = content.get("scope", "")
            expires = make_aware(expires)

            try:
                access_token = AccessToken.objects.select_related(
                    "application", "user"
                ).get(token=token)
            except AccessToken.DoesNotExist:
                access_token = AccessToken.objects.create(
                    token=token,
                    user=user,
                    application=None,
                    scope=scope,
                    expires=expires,
                )
            else:
                access_token.expires = expires
                access_token.scope = scope
                access_token.save()

            return access_token

    def validate_user(self, client, request, email, password, *args, **kwargs):
        """
        Check email and password correspond to a valid and active User
        """
        try:
            u = get_user_model().objects.get(email=request.email)
        except:  # pragma: no cover
            return False  # pragma: no cover

        if u.has_usable_password():
            u = authenticate(email=email, password=password)
            if u is not None and u.is_active:
                request.user = u
                return True
        elif not u.has_usable_password() and u.is_active and password == None:
            request.user = u
            return True

        return False  # pragma: no cover

    def authenticate_client(self, request, *args, **kwargs):  # pragma: no cover
        """
        Check if client exists and is authenticating itself as in rfc:`3.2.1`

        First we try to authenticate with HTTP Basic Auth, and that is the PREFERRED
        authentication method.
        Whether this fails we support including the client credentials in the request-body,
        but this method is NOT RECOMMENDED and SHOULD be limited to clients unable to
        directly utilize the HTTP Basic authentication scheme.
        See rfc:`2.3.1` for more details
        """

        authenticated = self._authenticate_basic_auth(request)

        if not authenticated:
            authenticated = self._authenticate_request_body(request)

        return authenticated
