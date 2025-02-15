from django.db import IntegrityError
from django.conf import settings
from django.db.models import Avg
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from rest_framework import (
    filters, mixins, permissions, status, viewsets
)
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import AccessToken

from .filters import TitleFieldsfilter
from .permissions import (
    AdminOrReadOnly, AuthorAdminModerator, SuperUserOrAdmin
)
from .serializers import (
    CategorySerializer, GenreSerializer, TitleSerializer,
    TitleReadOnlySerializer, ReviewSerializer, CommentSerializer,
    RegistratonSerializer, TokenSerializer, UserSerializer
)
from reviews.models import Category, Genre, Title
from users.models import User


class APIRegistration(APIView):
    """Регистрация пользователя."""
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        serializer = RegistratonSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            user, _ = User.objects.get_or_create(**serializer.validated_data)
            confirmation_code = default_token_generator.make_token(user)
            send_mail(
                'Subject here',
                f'Yor confirmation code: "{confirmation_code}"',
                settings.DEFAULT_FROM_EMAIL,
                [serializer.validated_data['email']],
                fail_silently=True,
            )
            return Response(serializer.validated_data,
                            status=status.HTTP_200_OK)
        except IntegrityError:
            if User.objects.filter(
                    username=serializer.validated_data['username']).exists():
                return Response(
                    {'username': ['Такое имя уже есть!']},
                    status=status.HTTP_400_BAD_REQUEST
                )
            if User.objects.filter(
                    email=serializer.validated_data['email']).exists():
                return Response(
                    {'email': ['Такое email уже есть!']},
                    status=status.HTTP_400_BAD_REQUEST
                )


class APIToken(APIView):
    """Получение JWT-токена."""
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        serializer = TokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data['username']
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response(
                {'username': ['Логин не найден']},
                status=status.HTTP_404_NOT_FOUND
            )

        confirmation_code = serializer.validated_data['confirmation_code']
        if not default_token_generator.check_token(
            user, confirmation_code
        ):
            return Response(
                {'confirmation_code': ['Некорректный код подтверждения!']},
                status=status.HTTP_400_BAD_REQUEST
            )
        token = AccessToken.for_user(user)
        return Response({'token': str(token)}, status=status.HTTP_200_OK)


class CreateListDestroyViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    """Миксин для вьюсетов Category и Genre"""
    pass


class TitleViewSet(viewsets.ModelViewSet):
    """Вьюсет для модели Title."""
    queryset = Title.objects.all().annotate(rating=Avg('reviews__score'))
    permission_classes = [AdminOrReadOnly, ]
    pagination_class = LimitOffsetPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFieldsfilter
    http_method_names = ('get', 'post', 'patch', 'delete')

    def get_serializer_class(self):
        if self.request.method in permissions.SAFE_METHODS:
            return TitleReadOnlySerializer
        return TitleSerializer


class CategoryViewSet(CreateListDestroyViewSet):
    """Вьюсет для модели Category."""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [AdminOrReadOnly, ]
    pagination_class = LimitOffsetPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'


class GenreViewSet(CreateListDestroyViewSet):
    """Вьюсет для модели Genre."""
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = [AdminOrReadOnly, ]
    pagination_class = LimitOffsetPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    pagination_class = LimitOffsetPagination
    permission_classes = [AuthorAdminModerator, ]
    http_method_names = ('get', 'post', 'patch', 'delete')

    def get_title(self):
        title_id = self.kwargs.get('title_id')
        return get_object_or_404(Title, id=title_id)

    def get_queryset(self):
        return self.get_title().reviews.all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, title=self.get_title())


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [AuthorAdminModerator, ]
    pagination_class = LimitOffsetPagination
    http_method_names = ('get', 'post', 'patch', 'delete')

    def get_title(self):
        title_id = self.kwargs.get('title_id')
        return get_object_or_404(Title, pk=title_id)

    def get_review(self):
        title = self.get_title()
        review_id = self.kwargs.get('review_id')
        review = get_object_or_404(title.reviews, pk=review_id)
        return review

    def get_queryset(self):
        return self.get_review().comments.all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, review=self.get_review())


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [SuperUserOrAdmin, ]
    pagination_class = LimitOffsetPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)
    lookup_field = 'username'
    http_method_names = ('get', 'post', 'patch', 'delete')

    @action(
        methods=['GET', 'PATCH'],
        detail=False,
        permission_classes=[permissions.IsAuthenticated],
        url_path='me'
    )
    def me(self, request):
        user = request.user
        if request.method == 'GET':
            serializer = UserSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        serializer = UserSerializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(role=user.role)
        return Response(serializer.data, status=status.HTTP_200_OK)
