from datetime import datetime
from django.db import models
from django.core.validators import (
    MaxValueValidator, MinValueValidator
)

from users.models import User

MIN_VALUE = 1
MAX_VALUE = 10


class Category(models.Model):
    name = models.CharField('Категория', max_length=256)
    slug = models.SlugField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Genre(models.Model):
    name = models.CharField('Жанр', max_length=256)
    slug = models.SlugField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Title (models.Model):
    name = models.CharField(
        max_length=256,
        verbose_name='Название произведения'
    )
    year = models.PositiveIntegerField(
        verbose_name='Год выхода',
        validators=[MaxValueValidator(int(datetime.now().year))],
    )
    description = models.TextField(blank=True, verbose_name='Описание')
    genre = models.ManyToManyField(
        Genre, related_name='titles',
        blank=True, verbose_name='Жанр'
    )
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL,
        related_name='titles',
        blank=True, null=True,
        verbose_name='Категория'
    )

    def __str__(self):
        return self.name


class Review(models.Model):
    """Модель отзыва"""
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='произведение'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Автор отзыва',
    )
    text = models.TextField()
    score = models.PositiveIntegerField(
        verbose_name='Оценка произведения',
        validators=[MinValueValidator(MIN_VALUE), MaxValueValidator(MAX_VALUE)]
    )
    pub_date = models.DateTimeField(
        'Дата добавления',
        auto_now_add=True
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['title', 'author'], name='unique_review'
            )
        ]

    def __str__(self):
        return self.text


class Comment(models.Model):
    """Модель комментария к отзыву"""
    text = models.TextField(verbose_name='Комментарий')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор комментария',
    )
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Комментарий к произведению'
    )
    pub_date = models.DateTimeField(
        'Дата добавления',
        auto_now_add=True
    )
