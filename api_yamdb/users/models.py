# from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.db import models

# User = get_user_model()


class User(AbstractUser):
    USER = 'user'
    MODERATOR = 'moderator'
    ADMIN = 'admin'
    ROLS = [(ADMIN, 'admin'), (MODERATOR, 'moderator'), (USER, 'user')]

    email = models.EmailField(
        max_length=254,
        verbose_name='Почта',
        unique=True
    )
    username = models.TextField(
        max_length=150,
        verbose_name='Имя пользователя',
        unique=True
    )
    role = models.CharField(
        max_length=25,
        verbose_name='Роль пользователя',
        choices=ROLS,
        default=USER
    )
    bio = models.TextField(verbose_name='Описание', null=True, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=~models.Q(username='me'),
                name='username_not_me'
            )
        ]

    @property
    def is_moderator(self):
        return self.role == 'moderator'

    @property
    def is_admin(self):
        return self.role == 'admin' or self.is_superuser

    def __str__(self):
        return self.username
