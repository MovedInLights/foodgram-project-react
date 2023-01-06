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

from .download_shopping_cart import download_shopping_cart
from .filters import RecipeFilter
from .serializers import (CustomSetPasswordSerializer, IngredientsSerializer,
                          RecipesSerializer, ShoppingCartSerializer,
                          TagSerializer, UserFollowSerializer,
                          UserRegistrationSerializer, UserSerializer)
from recipe.models import (Favorite, Ingredients, RecipeIngredients, Recipes,
                           ShoppingCart, Tags)
from users.models import Follow, User


class RegisterView(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        self.check_object_permissions(request)
        return Response(serializer.data)


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
    pagination_class = LimitOffsetPagination
    filter_backends = (DjangoFilterBackend, )
    filterset_class = RecipeFilter

    def create(self, request, **kwargs):
        data = request.data
        data['author'] = request.user.__dict__
        serializer = RecipesSerializer(data=data)
        if serializer.is_valid():
            new_recipe = Recipes.objects.create(
                author=request.user,
                name=data['name'],
                image=data['image'],
                text=data['text'],
                cooking_time=data['cooking_time'],
            )
            new_recipe.save()
            for ingredient in data['ingredients']:
                ingredient_obj = Ingredients.objects.get(id=ingredient['id'])
                RecipeIngredients.objects.create(
                    recipe=new_recipe,
                    related_ingredient=ingredient_obj,
                    quantity=ingredient['amount']
                )
                amount = ingredient['amount']
                ingredient_obj.amount = amount
                ingredient_obj.save()
                new_recipe.ingredients.add(ingredient_obj)

            for tag in data['tags']:
                tag_obj = Tags.objects.get(id=tag)
                new_recipe.tags.add(tag_obj)

            serializer = RecipesSerializer(new_recipe)

            return Response(serializer.data)
        return Response({
                "message": "The data isnt valid"
            }, status=status.HTTP_400_BAD_REQUEST)


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


class AllFollowingView(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request):

        request_user_id = request.user.id
        following_ids = User.objects.filter(following__user=request_user_id)
        serializer = UserFollowSerializer(following_ids, many=True)
        return Response(serializer.data)


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


class TagViewSet(
    mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet
):
    queryset = Tags.objects.all()
    serializer_class = TagSerializer
    permission_classes = (permissions.AllowAny,)
