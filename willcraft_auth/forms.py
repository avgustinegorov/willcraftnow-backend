from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import WillCraftUser


class WillCraftUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm):
        model = WillCraftUser
        fields = "__all__"


class WillCraftUserChangeForm(UserChangeForm):
    class Meta:
        model = WillCraftUser
        fields = "__all__"
