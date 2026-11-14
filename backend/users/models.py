from django.contrib.auth.models import AbstractUser
from django.db import models
from foodgram_backend.constants import (
    MAX_EMAIL_LENGTH,
    MAX_NAME_LENGTH,
    MAX_USERNAME_LENGTH,
)
from .validators import validate_username


class User(AbstractUser):
    """Пользователь с email в качестве имени входа, аватаром и подписками."""
    username = models.CharField(
        max_length=MAX_USERNAME_LENGTH,
        unique=True,
        validators=[validate_username],
        help_text='Не более 150 символов.',
    )
    email = models.EmailField(
        max_length=MAX_EMAIL_LENGTH,
        unique=True,
        help_text='Email для регистрации.',
    )
    first_name = models.CharField(
        max_length=MAX_NAME_LENGTH,
        blank=False,
        help_text='Ваше имя.'
    )
    last_name = models.CharField(
        max_length=MAX_NAME_LENGTH,
        blank=False,
        help_text='Ваша фамилия.'
    )
    avatar = models.ImageField(
        upload_to='users/avatars/',
        null=True,
        blank=True,
        verbose_name='Фото'
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username

    def is_admin(self):
        return self.is_staff


class Subscription(models.Model):
    """Связь «подписчик — автор» с уникальностью пары."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscriptions'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='followers'
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

    def __str__(self):
        return f'{self.user} подписан на {self.author}'
