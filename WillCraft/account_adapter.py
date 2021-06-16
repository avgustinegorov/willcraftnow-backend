from allauth.account.adapter import DefaultAccountAdapter
from django.conf import settings


class AccountAdapter(DefaultAccountAdapter):
    def is_open_for_signup(self, request):
        """
        Checks whether or not the site is open for signups.

        Next to simply returning True/False you can also intervene the
        regular flow by raising an ImmediateHttpResponse

        (Comment reproduced from the overridden method.)
        """
        if settings.SIGNUP_ALLOWED == "False":
            return False
        elif settings.SIGNUP_ALLOWED == "True":
            return True
        else:
            return False

    def render_mail(self, template_prefix, email, context):
        context["next_url"] = (
            "?next=%s" % self.request.path
        )  # <-- Append path to email context
        return super(AccountAdapter, self).render_mail(template_prefix, email, context)

    def get_email_confirmation_redirect_url(self, request):
        """
        The URL to return to after successful e-mail confirmation.
        """
        if request.user.is_authenticated:
            if request.GET.get("next"):  # <-- Check if request has 'next' parameter
                return request.GET.get("next")  # <-- Return the next parameter instead

            elif settings.EMAIL_CONFIRMATION_AUTHENTICATED_REDIRECT_URL:
                return settings.EMAIL_CONFIRMATION_AUTHENTICATED_REDIRECT_URL

            else:
                return self.get_login_redirect_url(request)
        else:
            return settings.EMAIL_CONFIRMATION_ANONYMOUS_REDIRECT_URL
