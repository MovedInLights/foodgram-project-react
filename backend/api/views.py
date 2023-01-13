import datetime

import jwt
from django.db import IntegrityError
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import mixins, permissions, status, viewsets
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.pagination import PageNumberPagination

from .download_shopping_cart import download_shopping_cart
from .filters import IngredientsFilter
from .serializers import (CustomSetPasswordSerializer, IngredientsSerializer,
                          RecipesSerializer, ShoppingCartSerializer,
                          TagSerializer, UserFollowSerializer,
                          UserRegistrationSerializer, UserSerializer, UserLogin)
from recipe.models import (Favorite, Ingredients, RecipeIngredients, Recipes,
                           ShoppingCart, Tags)
from users.models import Follow, User
from .pagination import CustomPagination


class RegisterView(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        self.check_object_permissions(request)
        return Response(serializer.data)


class CustomAuthToken(ObtainAuthToken):
    serializer_class = UserLogin

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                       context={'request': request})
        serializer.is_valid(raise_exception=True)
        email = request.data['email']
        password = request.data['password']
        user = User.objects.filter(email=email).first()
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'auth_token': token.key,
        })


class LoginView(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        email = request.data['email']
        password = request.data['password']

        user = User.objects.filter(email=email).first()
        if user is None:
            raise AuthenticationFailed('User not found')

        if not user.check_password(password):
            raise AuthenticationFailed('Incorrect password')

        payload = {
            'id': user.id,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=60),
            'iat': datetime.datetime.utcnow()
        }

        token = jwt.encode(payload, 'secret', algorithm='HS256')

        response = Response()

        response.set_cookie(key='auth_token', value=token)
        response.data = {
            'auth_token': token
        }
        return response


class LogoutView(APIView):
    def post(self, request):
        response = Response()
        response.delete_cookie('jwt')
        response.data = {
            'message': 'success'
        }
        return response


class UserCustomViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def get_serializer_class(self):
        if self.action == 'perform_create':
            return UserRegistrationSerializer
        if self.action == 'set_password':
            return CustomSetPasswordSerializer
        return UserSerializer


class RecipesViewSet(viewsets.ModelViewSet):
    queryset = Recipes.objects.all()
    serializer_class = RecipesSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        is_favorited = self.request.query_params.get('is_favorited')
        is_in_shopping_cart = self.request.query_params.get('is_in_shopping_cart')
        tags = self.request.query_params.getlist('tags')
        queryset = Recipes.objects.all()
        if is_favorited:
            favorite_id = Favorite.objects.filter(user=self.request.user).values_list('recipe', flat=True)
            queryset = Recipes.objects.filter(id__in=favorite_id)
        if is_in_shopping_cart:
            shopping_cart = ShoppingCart.objects.filter(user=self.request.user).values_list('recipe', flat=True)
            queryset = queryset.filter(id__in=shopping_cart)
        if tags:
            tags_id = Tags.objects.filter(slug__in=tags).values_list('id', flat=True)
            queryset = queryset.filter(tags__in=tags_id)
        return queryset


class FollowView(APIView):
    def post(self, request, **kwargs):

        user = request.user
        following_id = kwargs['pk1']
        if user.id == following_id:
            return Response({
                "message": "You cant follow self"
            }, status=status.HTTP_400_BAD_REQUEST)
        try:
            following = User.objects.get(pk=following_id)
            Follow.objects.create(user=user, following=following)
            following.is_subscribed = True
            serializer = UserFollowSerializer(following)
            return Response(serializer.data)
        except User.DoesNotExist:
            return Response({
                "message": "User doesnt exist"
            }, status=status.HTTP_400_BAD_REQUEST)
        except User.MultipleObjectsReturned:
            return Response({
                "message": "There are many users with that ID!"
            }, status=status.HTTP_400_BAD_REQUEST)
        except IntegrityError:
            return Response({
                "message": "Already subscribed"
            }, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):

        user = request.user
        following_id = kwargs['pk1']
        following = Follow.objects.filter(following_id=following_id, user=user)
        following.delete()
        following.is_subscribed = False
        return Response(status=status.HTTP_204_NO_CONTENT)


class ShoppingCartView(APIView):
    def post(self, request, **kwargs):

        user = request.user
        recipe_id = kwargs['pk1']
        recipe = Recipes.objects.get(pk=recipe_id)
        recipe.is_in_shopping_cart = True
        ShoppingCart.objects.create(
            user=user, recipe=recipe
        )
        serializer = ShoppingCartSerializer(recipe)
        return Response(serializer.data)

    def delete(self, request, *args, **kwargs):

        user = request.user
        recipe_id = kwargs['pk1']
        shopping_obj = ShoppingCart.objects.filter(
            recipe_id=recipe_id, user=user
        )
        shopping_obj.delete()
        shopping_obj.is_in_shopping_cart = False
        return Response(status=status.HTTP_204_NO_CONTENT)


class AllFollowingView(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserFollowSerializer
    permission_classes = (permissions.AllowAny,)
    pagination_class = PageNumberPagination

    def get_queryset(self):
        request_user_id = self.request.user
        following_ids = User.objects.filter(following__user=request_user_id)
        return following_ids


class DownloadShoppingCartView(APIView):
    def get(self, request):
        shopping_ids = ShoppingCart.objects.filter(
            user_id=self.request.user.id).values_list('recipe', flat=True
                                                      )
        # run dedicated function
        return download_shopping_cart(shopping_ids)


class FavoriteView(APIView):
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('tags',)

    def post(self, request, **kwargs):

        user = request.user
        recipe_id = kwargs['pk1']
        recipe = Recipes.objects.get(pk=recipe_id)
        recipe.is_favorited = True
        recipe.save()
        Favorite.objects.create(user=user, recipe=recipe)
        serializer = ShoppingCartSerializer(recipe)
        return Response(serializer.data)

    def delete(self, request, *args, **kwargs):
        user = request.user
        recipe_id = kwargs['pk1']
        favorite_recipe = Favorite.objects.filter(
            recipe_id=recipe_id, user=user
        )
        favorite_recipe.delete()
        favorite_recipe.is_favorited = False
        return Response(status=status.HTTP_204_NO_CONTENT)


class IngredientsViewSet(viewsets.ModelViewSet):
    queryset = Ingredients.objects.all()
    serializer_class = IngredientsSerializer
    permission_classes = (permissions.AllowAny,)
    pagination_class = None
    filter_backends = (DjangoFilterBackend, )
    filterset_class = IngredientsFilter


class TagViewSet(
    mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet
):
    pagination_class = None
    queryset = Tags.objects.all()
    serializer_class = TagSerializer
    permission_classes = (permissions.AllowAny,)
