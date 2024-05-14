from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models

from users.constants import MAX_LEN_USERNAME, MAX_LEN_EMAIL, MAX_LEN_PASSWORD

USER = 'user'
ADMIN = 'admin'

ROLES = ((USER, 'Аут. пользователь'),
         (ADMIN, 'Администратор'))


class User(AbstractUser):
    """Модель прользователей"""
    email = models.EmailField(
        verbose_name='Электронная почта',
        max_length=MAX_LEN_EMAIL,
        unique=True
    )
    username = models.CharField(
        verbose_name='Имя пользователя',
        max_length=MAX_LEN_USERNAME,
        unique=True,
        validators=[RegexValidator(
            regex=r'^[\w.@+-]+$',
            message='Недопустимый символ в имени пользователя'
        )])
    first_name = models.CharField(
        verbose_name='Имя',
        max_length=MAX_LEN_USERNAME
    )
    last_name = models.CharField(
        verbose_name='Фамилия',
        max_length=MAX_LEN_USERNAME
    )
    password = models.CharField(
        verbose_name='Пароль',
        max_length=MAX_LEN_PASSWORD
    )
    avatar = models.ImageField(
        verbose_name='Аватар',
        upload_to='users/avatars',
        blank=True
    )
    role = models.CharField(
        verbose_name='Пользовательская роль',
        max_length=15,
        choices=ROLES,
        default=USER
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name', 'password']

    class Meta:
        ordering = ('username',)
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return self.username


class Subscription(models.Model):
    """Модель подписки"""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscriber',
        verbose_name='Пользователь подписчик'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscribed',
        verbose_name='Автор рецепта'
    )
    subscription_date = models.DateTimeField(
        verbose_name='Дата подписки',
        auto_now_add=True
    )

    class Meta:
        ordering = ('subscription_date',)
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_user_subscription')]

    def __str__(self):
        return f'{self.user} подписался на {self.author}'
