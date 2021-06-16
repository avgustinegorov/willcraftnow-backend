from django.urls import path
from rest_auth.views import PasswordResetConfirmView

from .views import *

# from rest_auth.registration.views import VerifyEmailView

app_name = "willcraft_auth"

urlpatterns = [
    # URLs that require a user to be logged in with a valid session / token.
    # TODO: frontend JS code doesn't trigger this URL. Remove it when it is really not used anywhere.
    path("user/", UserDetailsView.as_view(), name="user_details"),
    path("logout/", LogoutView.as_view(), name="rest_logout"),
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="rest_login"),
    path("reset_password/", CustomPasswordResetView.as_view(), name="reset_password"),
    path(
        "reset_password_confirm/",
        CustomPasswordResetConfirmView.as_view(),
        name="reset_password_confirm",
    ),
    path("token_register/", TokenRegisterView.as_view(), name="token_register"),
    path("token_login/", TokenLoginView.as_view(), name="rest_token_login"),
    path("authorize/", AuthorizationView.as_view(), name="authorize"),
    path("introspect/", IntrospectTokenView.as_view(), name="introspect"),
    path("client_id/", GetClientId.as_view(), name="get-client-id"),
    path("client_whois/", GetClientNameView.as_view(), name="client_whois"),
    # path('token/refresh/', RefreshToken.as_view()),
    # path('token/revoke/', views.RevokeToken),
    # TODO: frontend JS code doesn't trigger this URL. Remove it when it is really not used anywhere.
    path("token/", TokenView.as_view(), name="create-token"),
    path("logged_in/", IntrospectTokenView.as_view(), name="logged-in"),
    path("is_user/", IfEmailIsRegisteredView.as_view(), name="is-user"),
    path("resend_token_email/", ResendTokenEmail.as_view(),
         name="resend-token-email"),
]
