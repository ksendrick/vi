import random
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from authapp.models import User
from django import forms
from django.contrib.auth import get_user_model

class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, item in self.fields.items():
            item.widget.attrs['class'] = 'form-control'


class RegisterForm(UserCreationForm):
    receive_notifications = forms.BooleanField(
        initial=True,
        required=False,
        label='Получать уведомления на почту',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

    class Meta:
        model = User
        fields = (
            'username',
            'password1',
            'password2',
            'first_name',
            'last_name',
            'phone_number',
            'email',
            'receive_notifications',
            'img'
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            field.help_text = ''
            field.widget.attrs['placeholder'] = ''

            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs['class'] = 'form-check-input'
            else:
                field.widget.attrs['class'] = 'form-control'

    def save(self, commit=True):
        user = super().save(commit=False)
        user.receive_notifications = self.cleaned_data['receive_notifications']
        if commit:
            user.save()
        return user



class UserEditForm(forms.ModelForm):
    receive_notifications = forms.BooleanField(
        required=False,
        label='Получать уведомления на почту',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

    class Meta:
        model = get_user_model()
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'img_banner', 'img', 'receive_notifications']
        labels = {
            'first_name': 'Имя',
            'last_name': 'Фамилия',
            'email': 'Электронная почта',
            'phone_number': 'Номер телефона',
            'img_banner': 'Баннер',
            'img': 'Аватар',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['receive_notifications'].initial = self.instance.receive_notifications
        for name, field in self.fields.items():
            field.help_text = ''
            field.widget.attrs['placeholder'] = ''
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs['class'] = 'form-check-input'
            else:
                field.widget.attrs['class'] = 'form-control'

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email != self.instance.email:
            self.instance.email_confirmed = False
            self.instance.email_confirmation_code = str(random.randint(100000, 999999))
            self.email_changed = True
        else:
            self.email_changed = False

        return email

    def save(self, commit=True):
        user = super().save(commit=False)

        if hasattr(self, 'email_changed') and self.email_changed:
            user.email_confirmed = False
            user.email_confirmation_code = str(random.randint(100000, 999999))

        if commit:
            user.save()
        return user
