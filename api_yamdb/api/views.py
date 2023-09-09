
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, permissions, viewsets, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import LimitOffsetPagination
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from rest_framework_simplejwt.tokens import AccessToken

from .filters import TitleFieldsfilter
from .permissions import (
    AdminOrReadOnly, AuthorAdminModerator, SuperUserOrAdmin
)
from .serializers import (
    CategorySerializer, GenreSerializer, TokenSerializer,
    TitleSerializer, TitleReadOnlySerializer, SignupSerializer,
    ReviewSerializer, CommentSerializer, UserSerializer
)
from reviews.models import Category, Genre, Title
from users.models import User


class TokenView(APIView):
    """Получение JWT-токена."""
    permission_classes = [permissions.AllowAny, ]

    def get_jwt_token(self, request):
        serializer = TokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = get_object_or_404(
            User,
            username=serializer.validated_data['username']
        )

        if default_token_generator.check_token(
            user, serializer.validated_data['confirmation_code']
        ):
            token = AccessToken.for_user(user)
            return Response({'token': str(token)}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [SuperUserOrAdmin, ]
    pagination_class = LimitOffsetPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)
    http_method_names = ('get', 'post', 'patch', 'delete')


class SignupView(APIView):
    """Регистрация пользователя."""
    permission_classes = [permissions.AllowAny, ]

    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        username = serializer.validated_data['username']
        user, create = User.objects.get_or_create(username=username,
                                                  email=email)
        confirmation_code = default_token_generator.make_token(user)
        user.confirmation_code = confirmation_code
        user.save()
        send_mail(
            subject='Confirmation code',
            message=f'Your confirmation code: {confirmation_code}',
            from_email=None,
            recipient_list=[user.email],
        )

        return Response(serializer.data, status=status.HTTP_200_OK)


class TitleViewSet(viewsets.ModelViewSet):
    """Вьюсет для модели Title."""
    queryset = Title.objects.all()
    permission_classes = [AdminOrReadOnly, ]
    pagination_class = LimitOffsetPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFieldsfilter
    http_method_names = ('get', 'post', 'patch', 'delete')

    def get_serializer_class(self):
        if self.request.method in permissions.SAFE_METHODS:
            return TitleReadOnlySerializer
        return TitleSerializer


class CreateListDestroyViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    """Миксин для вьюсетов Category и Genre"""
    pass


class CategoryViewSet(CreateListDestroyViewSet):
    """Вьюсет для модели Category."""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [AdminOrReadOnly, ]
    pagination_class = LimitOffsetPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)


class GenreViewSet(CreateListDestroyViewSet):
    """Вьюсет для модели Genre."""
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = [AdminOrReadOnly, ]
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [AuthorAdminModerator, ]

    def get_title(self):
        # title_id = self.kwargs.get('title_id')
        # return get_object_or_404(Title, pk=title_id)
        return get_object_or_404(Title, id=self.kwargs.get('title_id'))

    def get_queryset(self):
        return self.get_title().reviews.all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, title=self.get_title())


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [AuthorAdminModerator, ]

    def get_title(self):
        title_id = self.kwargs.get('title_id')
        return get_object_or_404(Title, id=title_id)

    def get_review(self):
        title = self.get_title()
        review_id = self.kwargs.get('review_id')
        review = title.reviews.get(pk=review_id)
        return review

    def get_queryset(self):
        return self.get_review().comments.all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, review=self.get_review())
