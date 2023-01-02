from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path, re_path
from rest_framework.authtoken import views
from rest_framework.routers import DefaultRouter

from .views import (AllFollowingView, DownloadShoppingCartView, FavoriteView,
                    FollowView, IngredientsViewSet, LogoutView, RecipesViewSet,
                    RegisterView, ShoppingCartView, TagViewSet,
                    UserCustomViewSet)

router_v1 = DefaultRouter()

router_v1.register('tags', TagViewSet)
router_v1.register('recipes', RecipesViewSet)
router_v1.register('ingredients', IngredientsViewSet)
router_v1.register('users', UserCustomViewSet)


urlpatterns = [
    re_path(r'^auth/', include('djoser.urls')),
    re_path(r'^auth/', include('djoser.urls.jwt')),
    path('', include(router_v1.urls)),
    path('users/', RegisterView.as_view()),
    path('users/<int:pk1>/subscribe/', FollowView.as_view()),
    path('recipes/<int:pk1>/shopping_cart/', ShoppingCartView.as_view()),
    path('recipes/download_shopping_cart', DownloadShoppingCartView.as_view()),
    path('recipes/<int:pk1>/favorite/', FavoriteView.as_view()),
    path('users/subscriptions', AllFollowingView.as_view()),
    path('auth/token/login/', views.obtain_auth_token, name='login'),
    path('auth/token/logout/', LogoutView.as_view(), name='logout'),
]
if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )
