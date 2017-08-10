from django import forms
from django.contrib.auth.forms import UserCreationForm

from app_users.models import User, Profile


class UserForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        css_class = {'class': "form-control"}
        self.fields['username'].widget.attrs.update(css_class)
        self.fields['email'].widget.attrs.update(css_class)
        self.fields['password1'].widget.attrs.update(css_class)
        self.fields['password2'].widget.attrs.update(css_class)

    class Meta:
        model = User
        fields = ('username', 'password1', 'password2', 'email',)


class ProfileForm(forms.ModelForm):
    css_class = {'class': "form-control"}

    def __init__(self, *args, **kwargs):
        css_class = {'class': "form-control"}
        super(ProfileForm, self).__init__(*args, **kwargs)
        self.fields['referral_code'].widget.attrs.update(css_class)

    class Meta:
        model = Profile
        fields = ('referral_code',)
