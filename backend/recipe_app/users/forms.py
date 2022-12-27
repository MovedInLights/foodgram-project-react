# users/forms
from django.contrib.auth.forms import UserCreationForm
from django.forms import ModelForm

from .models import User


class CreationForm(UserCreationForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].label = 'Пароль'
        self.fields['password2'].label = 'Подтверждение пароля'
        self.fields['password1'].help_text = '8 символов минимум'
        self.fields['password2'].help_text = 'Пароли должны совпадать'

        for field in self.fields:
            self.fields[str(field)].widget.attrs.update(
                {'class': 'form-control'}
            )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('login',)


class UserForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[str(field)].widget.attrs.update(
                {'class': 'form-control'}
            )

    class Meta:
        model = User
        fields = [
            'email',
            'first_name',
            'last_name',
            'login',
        ]


class CreateUserForm(ModelForm):

    class Meta:
        model = User
        fields = [
            'email',
            'first_name',
            'last_name',
            'login',
        ]
