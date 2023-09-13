from datetime import datetime

from django.db.models import Avg
from rest_framework import serializers
from rest_framework.generics import get_object_or_404

from reviews.models import Category, Genre, Title, Review, Comment
from users.validators import me_username_validator, username_validator
from users.models import User


class RegistratonSerializer(serializers.Serializer):
    username = serializers.CharField(
        required=True, max_length=150,
        validators=[me_username_validator, username_validator],
    )
    email = serializers.EmailField(required=True, max_length=254)
    first_name = serializers.CharField(max_length=150, required=False)
    last_name = serializers.CharField(max_length=150, required=False)
    bio = serializers.CharField(max_length=24, required=False)

    def validate_username(self, value):
        if User.objects.filter(username=value):
            raise serializers.ValidationError(
                f'Пользователь с именем {value} уже есть!'
            )
        return value

    def validate_email(self, value):
        if User.objects.filter(email=value):
            raise serializers.ValidationError(
                f'Пользователь с почтой {value} уже есть!'
            )
        return value


class TokenSerializer(serializers.Serializer):
    username = serializers.CharField(required=True, max_length=150)
    confirmation_code = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = (
            'username',
            'confirmation_code'
        )


class ReviewSerializer(serializers.ModelSerializer):
    """Сериализатор для Review модели"""
    author = serializers.SlugRelatedField(
        read_only=True, default=serializers.CurrentUserDefault(),
        slug_field='username'
    )

    class Meta:
        fields = ('id', 'text', 'author', 'score', 'pub_date')
        model = Review

    def validate(self, data):
        author = self.context['request'].user
        title_id = self.context['view'].kwargs.get('title_id')
        title = get_object_or_404(Title, pk=title_id)
        if self.context['request'].method == 'POST':
            if Review.objects.filter(title=title, author=author).exists():
                raise serializers.ValidationError('Только один отзыв!')
        return data


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username'
    )

    class Meta:
        fields = ('id', 'text', 'author', 'pub_date')
        model = Comment


class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор для модели Category."""
    class Meta:
        model = Category
        fields = ('name', 'slug')


class GenreSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Genre."""
    class Meta:
        model = Genre
        fields = ('name', 'slug')


class TitleSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Title."""
    category = serializers.SlugRelatedField(
        queryset=Category.objects.all(),
        slug_field='slug',
    )
    genre = serializers.SlugRelatedField(
        many=True,
        queryset=Genre.objects.all(),
        slug_field='slug',
    )
    rating = serializers.SerializerMethodField()

    class Meta:
        model = Title
        fields = (
            'id', 'name', 'year', 'rating',
            'description', 'genre', 'category'
        )

    def validate_year(self, value):
        if value >= datetime.now().year:
            raise serializers.ValidationError(
                'Год выхода должен быть не позже текущего!')
        return value

    def get_rating(self, obj):
        rating = Review.objects.filter(
            title=obj.id).aggregate(Avg('score'))
        return rating


class TitleReadOnlySerializer(serializers.ModelSerializer):
    """Сериализатор GET-запросов для модели Title."""
    category = CategorySerializer(read_only=True)
    genre = GenreSerializer(many=True, read_only=True)
    rating = serializers.IntegerField(read_only=True)

    class Meta:
        model = Title
        fields = (
            'id', 'name', 'year', 'rating',
            'description', 'genre', 'category'
        )


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name', 'last_name', 'bio', 'role'
        )
