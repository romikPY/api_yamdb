from django.contrib.auth.models import AbstractUser
from django.db import models

from .validators import me_username_validator, username_validator


class User(AbstractUser):
    USER = 'user'
    MODERATOR = 'moderator'
    ADMIN = 'admin'
    ROLES = [
        (ADMIN, 'admin'),
        (MODERATOR, 'moderator'),
        (USER, 'user')
    ]

    username = models.CharField(
        max_length=150,
        verbose_name='Имя пользователя',
        unique=True,
        validators=[me_username_validator, username_validator],
    )

    email = models.EmailField(
        max_length=254,
        verbose_name='Почта',
        unique=True
    )

    role = models.CharField(
        max_length=25,
        verbose_name='Роль пользователя',
        choices=ROLES,
        default=USER
    )
    bio = models.TextField(
        verbose_name='Описание',
        blank=True
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=~models.Q(username='me'),
                name='username_not_me'
            )
        ]

    def __str__(self):
        return self.username

    @property
    def is_moderator(self):
        return self.role == 'moderator'

    @property
    def is_admin(self):
        return self.role == 'admin' or self.is_superuser
