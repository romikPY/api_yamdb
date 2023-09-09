from datetime import datetime

from django.db.models import Avg
from rest_framework import serializers
from rest_framework.generics import get_object_or_404
from rest_framework.validators import UniqueTogetherValidator, UniqueValidator

from reviews.models import Category, Genre, Title, Review, Comment, User


class UserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        required=True, max_length=150,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    email = serializers.EmailField(required=True, max_length=254)

    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name', 'last_name', 'bio', 'role'
        )


class SignupSerializer(serializers.Serializer):
    """Регистрация пользователя."""
    email = serializers.EmailField(max_length=254, required=True)
    username = serializers.RegexField(max_length=150,
                                      required=True,
                                      regex=r'^[\w.@+-]+$')

    class Meta:
        fields = ('username', 'email', 'role')

    def validate(self, data):
        if data.get('username') == 'me':
            raise serializers.ValidationError
        if (User.objects.filter(username=data.get('username'))
           and User.objects.filter(email=data.get('email'))):
            return data
        if User.objects.filter(username=data.get('username')):
            raise serializers.ValidationError('Пользователь с таким username '
                                              'уже существует.')

        if User.objects.filter(email=data.get('email')):
            raise serializers.ValidationError('Пользователь с таким email '
                                              'уже существует.')
        return data


class ReviewSerializer(serializers.ModelSerializer):
    """Сериализатор для Review модели"""
    title = serializers.SlugRelatedField(
        slug_field='name',
        read_only=True
    )
    auhor = serializers.SlugRelatedField(
        read_only=True, default=serializers.CurrentUserDefault(),
        slug_field='username'
    )

    class Meta:
        fields = '__all__'
        model = Review

        validators = [
            UniqueTogetherValidator(
                queryset=Review.objects.all(),
                fields=['author', 'title']
            )
        ]

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

    class Meta:
        model = Title
        fields = '__all__'
        # fields = (
        #    'name', 'year', 'description', 'genre', 'category'
        # )

        def validate_year(self, value):
            if value >= datetime.now().year:
                raise serializers.ValidationError(
                    'Год выхода должен быть не позже текущего')
            return value


class TitleReadOnlySerializer(serializers.ModelSerializer):
    """Сериализатор GET-запросов для модели Title."""
    category = CategorySerializer(read_only=True)
    genre = GenreSerializer(many=True, read_only=True)
    rating = serializers.SerializerMethodField()

    class Meta:
        model = Title
        fields = (
            'id', 'name', 'year', 'rating',
            'description', 'genre', 'category'
        )

    def get_rating(self, obj):
        rating = Review.objects.filter(
            title=obj.id).aggregate(Avg('score'))
        return rating['score__avg']


class UserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        required=True, max_length=150,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    email = serializers.EmailField(required=True, max_length=254)

    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name', 'last_name', 'bio', 'role'
        )


class TokenSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    confirmation_code = serializers.CharField(required=True)
