from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator, FileExtensionValidator
from django.db import models
from django.contrib.auth.validators import ASCIIUsernameValidator


class User(AbstractUser):
    username_validator = ASCIIUsernameValidator()
    username = models.CharField(
        verbose_name='Логин',
        max_length=150,
        unique=True,
        validators=[username_validator],
    )
    first_name = models.CharField(
        verbose_name='Имя',
        max_length=50,
        validators=[
            RegexValidator(
                regex='^[А-Яа-яЁё]+$',
                message='Используйте только русские символы.'
            )
        ],
        null=True
    )
    last_name = models.CharField(
        verbose_name='Фамилия',
        max_length=50,
        validators=[
            RegexValidator(
                regex='^[А-Яа-яЁё]+$',
                message='Используйте только русские символы.'
            )
        ],
        null=True
    )
    email_confirmed = models.BooleanField(default=False, verbose_name='Почта подтверждена')
    email_confirmation_code = models.CharField(max_length=6, blank=True, null=True)
    email = models.EmailField(verbose_name='Почта', max_length=150, unique=True)
    receive_notifications = models.BooleanField(default=True, verbose_name='Получать уведомления')
    phone_number = models.CharField(verbose_name='Номер телефона', max_length=20, null=True)
    img_banner = models.ImageField(verbose_name='Баннер', upload_to='banner/%Y/%m/%d', default='../static/img/fon.jpg',
                                   validators=[FileExtensionValidator(['png', 'jpeg', 'jpg']
                                                                      )], null=True)
    img = models.ImageField(verbose_name='Аватар', upload_to='avatar/%Y/%m/%d', default='avatar/avatar.jpg',
                            validators=[FileExtensionValidator(
                                ['png', 'jpeg', 'jpg']
                            )], null=True)

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        db_table = 'user'
