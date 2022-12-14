from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from djoser.serializers import UserCreateSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from recipes.models import (
    Favourite, Ingredient, IngredientForRecipe,
    Recipe, ShoppingList, Tag
)
from users.models import Subscription

User = get_user_model()


class CustomUserCreateSerializer(UserCreateSerializer):
    email = serializers.EmailField(
        max_length=254,
        validators=[UniqueValidator(queryset=User.objects.all())])
    username = serializers.CharField(
        max_length=150,
        validators=[UniqueValidator(queryset=User.objects.all())])
    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150)

    class Meta:
        model = User
        fields = (
            'email',
            'username',
            'first_name',
            'last_name',
            'password',
        )
        extra_kwargs = {
            'email': {'required': True},
            'username': {'required': True},
            'password': {'required': True}
        }

    def create(self, validated_data):
        user = User(
            email=validated_data['email'],
            username=validated_data['username'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


class CustomUserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
        )

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if not user.is_authenticated:
            return False
        return Subscription.objects.filter(user=user, author=obj).exists()


class TagSerializer(serializers.ModelSerializer):

    """???????????????????????? ?????? ?????????????????? ??????????"""
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    """???????????????????????? ?????? ?????????????????? ????????????????????????"""
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class IngredientForRecipeSerializer(serializers.ModelSerializer):
    """???????????????????????? ?????? ???????????????????????? ??????????????"""
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit')

    class Meta:
        model = IngredientForRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')


class ShortRecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField()
    """???????????????? ???????????? ?????????????? ?????? ???????????????????? ?? ??????????????"""

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = ('id', 'name', 'image', 'cooking_time')


class RecipeSerializer(serializers.ModelSerializer):
    """???????????????????????? ?????? ????????????????"""
    author = CustomUserSerializer(read_only=True)
    ingredients = IngredientForRecipeSerializer(
        many=True,
        source='ingredient_for_recipe',
        read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time'
        )

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        user = request.user
        return (
            user.is_authenticated
            and Favourite.objects.filter(
                user=user,
                recipe=obj,
            ).exists()
        )

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        user = request.user
        return (
            user.is_authenticated
            and ShoppingList.objects.filter(
                user=user,
                recipe=obj,
            ).exists()
        )


class RecipeCreateSerializer(serializers.ModelSerializer):
    """???????????????????????? ?????? ???????????????? ????????????????"""
    tags = TagSerializer(many=True, read_only=True)
    image = Base64ImageField()
    ingredients = IngredientForRecipeSerializer(
        many=True,
        source='ingredient_for_recipe',
        read_only=True)
    author = CustomUserSerializer(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'name',
            'image',
            'text',
            'cooking_time'
        )

    def validate(self, data):
        name = str(self.initial_data.get('name')).strip()
        ingredients = self.initial_data.get('ingredients')
        if not ingredients:
            raise serializers.ValidationError({
                'ingredients': '???????????????? ??????????????????????!'})
        ingredients_set = set()
        for ingredient in ingredients:
            if int(ingredient.get('amount')) <= 0:
                raise serializers.ValidationError(
                    '???????????????????? ?????????????????????? ???????????? ???????? ???????????? 0!')
            id = ingredient.get('id')
            if id in ingredients_set:
                raise serializers.ValidationError(
                    '???????? ???????????????????? ???? ?????? ??????????????!')
            ingredients_set.add(id)
        data['name'] = name.capitalize()
        data['ingredients'] = ingredients
        return data

    def create(self, validated_data):
        tags = self.initial_data.get('tags')
        image = validated_data.pop('image')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(
            **validated_data,
            image=image,
            author=self.context.get('request').user
        )
        for tag in tags:
            recipe.tags.add(get_object_or_404(Tag, pk=tag))
        ingredient_list = [
            IngredientForRecipe(
                recipe=recipe,
                ingredient_id=ingredient.get('id'),
                amount=ingredient.get('amount')
            )
            for ingredient in ingredients
        ]
        IngredientForRecipe.objects.bulk_create(objs=ingredient_list)
        return recipe

    def update(self, recipe, validated_data):
        recipe.tags.clear()
        tags = self.initial_data.get('tags')
        ingredients = validated_data.get('ingredients')
        recipe.image = validated_data.get(
            'image', recipe.image)
        recipe.name = validated_data.get(
            'name', recipe.name)
        recipe.text = validated_data.get(
            'text', recipe.text)
        recipe.cooking_time = validated_data.get(
            'cooking_time', recipe.cooking_time)
        for tag in tags:
            recipe.tags.add(get_object_or_404(Tag, pk=tag))
        if ingredients:
            recipe.ingredients.clear()
            ingredient_list = [
                IngredientForRecipe(
                    recipe=recipe,
                    ingredient=get_object_or_404(
                        Ingredient, pk=ingredient.get('id')
                    ),
                    amount=ingredient.get('amount')
                )
                for ingredient in ingredients
            ]
            IngredientForRecipe.objects.bulk_create(objs=ingredient_list)
        recipe.save()
        return recipe


class SubscribeSerializer(serializers.ModelSerializer):
    """???????????????????????? ?????? ???????????????? ?????????? ????????????????"""
    class Meta:
        model = Subscription
        fields = ['id', 'user', 'author']

    def validate(self, data):
        author = data['author']
        user = data['user']
        if user == author:
            raise serializers.ValidationError({
                'errors': '???????????? ?????????????????????? ???? ????????'}
            )
        if Subscription.objects.filter(user=user, author=author).exists():
            raise serializers.ValidationError({
                'errors': '???? ?????? ?????????????????????? ???? ?????????? ????????????????????????'}
            )
        return data


class SubscriptionSerializer(serializers.ModelSerializer):
    """???????????????????????? ?????? ????????????????"""
    id = serializers.ReadOnlyField(source='author.id')
    email = serializers.ReadOnlyField(source='author.email')
    username = serializers.ReadOnlyField(source='author.username')
    first_name = serializers.ReadOnlyField(source='author.first_name')
    last_name = serializers.ReadOnlyField(source='author.last_name')
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = Subscription
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
        )

    def get_is_subscribed(self, obj):
        return Subscription.objects.filter(
            user=obj.user, author=obj.author
        ).exists()

    def get_recipes(self, obj):
        request = self.context.get('request')
        limit = request.query_params.get('recipes_limit')
        queryset = Recipe.objects.filter(author=obj.author)
        if limit:
            queryset = queryset[:int(limit)]
        return ShortRecipeSerializer(queryset, many=True).data

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj.author).count()


class FavouriteSerializer(serializers.ModelSerializer):
    """???????????????????????? ?????? ?????????????????? ????????????????"""
    class Meta:
        model = Favourite
        fields = ('id', 'user', 'recipe')

    def validate(self, data):
        request = self.context.get('request')
        recipe = data['recipe']
        if Favourite.objects.filter(user=request.user, recipe=recipe).exists():
            raise serializers.ValidationError(
                {'errors': '???????????? ?????? ???????????????? ?? ??????????????????!'}
            )
        return data


class ShoppingListSerializer(serializers.ModelSerializer):
    """???????????????????????? ?????? ???????????? ??????????????"""
    class Meta:
        model = ShoppingList
        fields = ('id', 'user', 'recipe')

    def validate(self, data):
        request = self.context.get('request')
        recipe = data['recipe']
        if ShoppingList.objects.filter(user=request.user,
                                       recipe=recipe).exists():
            raise serializers.ValidationError(
                {'errors': '???????????? ?????? ???????????????? ?? ???????????? ??????????????!'}
            )
        return data
