import base64

import webcolors
from django.core.files.base import ContentFile
from djoser.serializers import SetPasswordSerializer, UserCreateSerializer
from rest_framework import serializers

from recipe.models import Ingredients, Recipes, Tags
from users.models import Follow, User


class Name2Hex(serializers.Field):
    def to_representation(self, value):
        return value

    def to_internal_value(self, data):
        try:
            data = webcolors.name_to_hex(data)
        except ValueError:
            raise serializers.ValidationError('No such color')
        return data


class Picture2Text(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'password',
            'username',
            'first_name',
            'last_name',
            'is_subscribed'
        )
        extra_kwargs = {
            'username': {'required': True, 'allow_blank': False},
            'email': {'required': True, 'allow_blank': False},
            'password': {
                'required': True,
                'allow_blank': False,
                "write_only": True
            },
            'first_name': {'required': True, 'allow_blank': False},
            'last_name': {'required': True, 'allow_blank': False}
        }

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance


class UserRegistrationSerializer(UserCreateSerializer):
    def perform_create(self, validated_data):
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance


class FollowSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
        default=serializers.CurrentUserDefault()
    )
    following = serializers.SlugRelatedField(
        slug_field='username',
        queryset=User.objects.all()
    )

    class Meta:
        model = Follow
        fields = ('user', 'following')

    def validate(self, data):
        if self.context['request'].user == data['following']:
            raise serializers.ValidationError(
                'Попытка подписаться на самого себя'
            )
        return data


class CustomSetPasswordSerializer(SetPasswordSerializer):

    class Meta:
        model = User
        fields = ('new_password', 'current_password',)


class TagSerializer(serializers.ModelSerializer):
    color = Name2Hex()
    id = serializers.PrimaryKeyRelatedField(required=False, read_only=True)

    class Meta:
        model = Tags
        fields = ('id', 'name', 'color', 'slug')
        extra_kwargs = {'id': {'read_only': False}}


class IngredientsSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()

    class Meta:
        fields = ('id', 'name', 'measurement_unit', 'amount')
        model = Ingredients
        extra_kwargs = {"name": {"required": False, "allow_null": True},
                        "measurement_unit": {
                            "required": False,
                            "allow_null": True
                        }}


class IngredientsSerializerRecipes(serializers.ModelSerializer):

    class Meta:
        fields = ('id', 'amount')
        model = Ingredients


class RecipesSerializer(serializers.ModelSerializer):
    author = UserSerializer()
    image = Picture2Text(required=False, allow_null=True, read_only=True)
    ingredients = IngredientsSerializer(many=True, required=False)

    class Meta:
        model = Recipes
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def update(self, instance, validated_data):

        ingredients = validated_data.get('ingredients')
        tags = validated_data.get('tags')
        instance.ingredients.clear()
        instance.tags.clear()

        for ingredient in ingredients:
            ingredient, created = Ingredients.objects.get_or_create(
                id=ingredient['id']
            )
            instance.ingredients.add(ingredient)

        for tag in tags:
            tag = Tags.objects.get(id=tag.id)
            instance.tags.add(tag)

        instance.save()
        return instance


class RecipesSerializerRestricted(serializers.ModelSerializer):

    class Meta:
        model = Recipes
        fields = (
            'id',
            'name',
            'image',
            'cooking_time',
        )


class UserFollowSerializer(serializers.ModelSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    def get_recipes_count(self, obj):
        following_user = User.objects.get(id=obj.id)
        recipes_obj = Recipes.objects.filter(author_id=following_user.id)
        return recipes_obj.count()

    def get_recipes(self, obj):
        following_user = User.objects.get(id=obj.id)
        recipes_obj = Recipes.objects.filter(author_id=following_user.id)
        return RecipesSerializerRestricted(recipes_obj, many=True).data

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count'
        )


class ShoppingCartSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipes
        fields = ('id', 'name', 'image', 'cooking_time')
