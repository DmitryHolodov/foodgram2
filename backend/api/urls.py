from django.urls import include, path
from rest_framework.routers import DefaultRouter

from users.views import SignUpView, UserViewSet


router = DefaultRouter()
router.register(r'users', UserViewSet, basename='users')


urlpatterns = [
    path('', include(router.urls)),
    path(
        'auth/signup/',
        SignUpView.as_view(),
        name='signup',
    ),
    # path(
    #     'auth/token/',
    #     TokenView.as_view(),
    #     name='token',
    # ),
]
