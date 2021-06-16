from oauth2_provider.models import get_access_token_model  # pragma: no cover


class GetUserTokenMixin:  # pragma: no cover
    def get_token(self, token=None, *args, **kwargs):
        try:
            token_value = token
            if token_value == None:
                token_value = self.kwargs["token"]
            token = get_access_token_model().objects.get(token=token_value)
        except:
            print(f"Token Not Found.")
        else:
            if token.is_expired():
                print(f"Token Expired.")
            else:
                return token

    def get_user(self, token=None, *args, **kwargs):
        token = self.get_token(token=token)
        return token.user

    def get_firm(self, token=None, *args, **kwargs):
        user = self.get_user(token=token)
        try:
            firm = Firm.objects.get(user=user)
        except:
            print(f"User is not related to a Firm.")
        return firm
