import base64
from users.models import Follow, User
from recipe.models import Ingredients, RecipeIngredients, Recipes, Tags

import webcolors
from django.core.files.base import ContentFile
from djoser.serializers import SetPasswordSerializer, UserCreateSerializer
from rest_framework import serializers
from collections import OrderedDict


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


class UserLogin(serializers.ModelSerializer):
    email = serializers.CharField(
        write_only=True
    )
    password = serializers.CharField(
        write_only=True
    )

    class Meta:
        model = User
        fields = (
            'email',
            'password',
        )


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


class TagWithinRecipeSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()

    class Meta:
        fields = ('id', 'name', 'color', 'slug')
        model = Tags


class UserRecipeSerializer(serializers.ModelSerializer):

    class Meta:
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed'
        )
        model = User


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
        fields = ('id', 'amount', 'measurement_unit')
        model = Ingredients


class RecipesSerializer(serializers.ModelSerializer):
    author = UserRecipeSerializer(many=False, read_only=True)
    image = Picture2Text(required=False, allow_null=True, read_only=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tags.objects.all(), many=True
    )
    ingredients = IngredientsSerializer(
        many=True, required=False, partial=True
    )

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

    def create(self, validated_data):
        new_recipe = Recipes.objects.create(
            author=self.context['request'].user,
            name=validated_data['name'],
            image=validated_data['image'],
            text=validated_data['text'],
            cooking_time=validated_data['cooking_time'],
        )
        new_recipe.save()

        for ingredient in validated_data['ingredients']:
            ingredient_obj = Ingredients.objects.get(id=ingredient['id'])
            RecipeIngredients.objects.create(
                recipe=new_recipe,
                ingredients=ingredient_obj,
                amount=ingredient['amount']
            )
            amount = ingredient['amount']
            ingredient_obj.amount = amount
            ingredient_obj.save()
            new_recipe.ingredients.add(ingredient_obj)

        for tag in validated_data['tags']:
            tag_obj = Tags.objects.get(**tag)
            new_recipe.tags.add(tag_obj)

        new_recipe.save()
        return new_recipe

    def update(self, instance, validated_data):

        ingredients = validated_data.get('ingredients')
        tags = validated_data.get('tags')
        instance.ingredients.clear()
        instance.tags.clear()
        for ingredient in ingredients:

            RecipeIngredients.objects.update_or_create(
                related_ingredient_id=ingredient['id'],
                recipe_id=instance.id,
                quantity=ingredient['amount']
            )
            instance.ingredients.add(ingredient['id'])

        for tag in tags:
            tag = Tags.objects.get(id=tag.id)
            instance.tags.add(tag)
        instance.save()
        return instance

    def validate_ingredients(self, data):
        ingredients = []
        for items in data:
            ingredients.append(items['id'])
        if len(ingredients) != len(set(ingredients)):
            raise serializers.ValidationError(
                'Some ingredients are duplicated. '
                'Please check your data'
            )
        return data

    def to_representation(self, obj):
        tags_serialized = TagWithinRecipeSerializer(obj.tags, many=True).data
        representation = super().to_representation(obj)
        representation['tags'] = tags_serialized
        return representation


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

    def validate_following(self, data):
        if self.context['request'].user == data['following']:
            raise serializers.ValidationError(
                'Self follow attempt'
            )
        return data


class ShoppingCartSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipes
        fields = ('id', 'name', 'image', 'cooking_time')
