from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    CategoryViewSet, GenreViewSet, TitleViewSet,
    CommentViewSet, ReviewViewSet, APIRegistration,
    APIToken, UserViewSet
)

v1_router = DefaultRouter()

v1_router.register(r'users', UserViewSet, basename='users')
v1_router.register(r'titles/(?P<title_id>\d+)/reviews',
                   ReviewViewSet, basename='reviews')
v1_router.register(r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)'
                   r'/comments', CommentViewSet, basename='comments')

v1_router.register(
    r'categories', CategoryViewSet, basename='categories'
)
v1_router.register(
    r'genres', GenreViewSet, basename='genres'
)
v1_router.register(
    r'titles', TitleViewSet, basename='titles'
)

urlpatterns = [
    path('v1/', include(v1_router.urls)),
    path('v1/auth/signup/', APIRegistration.as_view(), name='signup'),
    path('v1/auth/token/', APIToken.as_view(), name='send_token'),
]
