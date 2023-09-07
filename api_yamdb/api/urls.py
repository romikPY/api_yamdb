from django.urls import path, include
from rest_framework.routers import DefaultRouter

from api.views import CommentViewSet, ReviewViewSet, UserViewSet
from .views import (
    CategoryViewSet, GenreViewSet, TitleViewSet
)

v1_router = DefaultRouter()

v1_router.register(r'users', UserViewSet, basename='users')
v1_router.register(r'titles/(?P<title_id>/reviews)',
                   ReviewViewSet, basename='reviews')
v1_router.register(r'titles/(?P<title_id>)/reviews/(?P<review_id>)/comments',
                   CommentViewSet, basename='comments')

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
    # path('v1/auth/signup/', signup, name='signup'),
    # path('v1/auth/token/', send_token, name='send_token'),
]
