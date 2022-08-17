from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from drf_extra_fields.fields import Base64ImageField
from recipes.models import (Favourite, Ingredient, IngredientForRecipe, Recipe,
                            ShoppingList, Tag)
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from users.models import Subscription

User = get_user_model()


class CustomUserCreateSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        validators=[UniqueValidator(queryset=User.objects.all())])
    username = serializers.CharField(
        validators=[UniqueValidator(queryset=User.objects.all())])
    first_name = serializers.CharField()
    last_name = serializers.CharField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password',
        )
        extra_kwargs = {
            "email": {"required": True},
            "first_name": {"required": True},
            "last_name": {"required": True},
        }


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
    """Сериализатор для просмотра тегов"""
    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для просмотра ингредиентов"""
    class Meta:
        model = Ingredient
        fields = '__all__'


class IngredientForRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для ингредиентов рецепта"""
    id = serializers.PrimaryKeyRelatedField(
        source='ingredient.id', queryset=Ingredient.objects.all()
    )
    name = serializers.ReadOnlyField(source='ingredient.name')
    measure_unit = serializers.ReadOnlyField(
        source='ingredient.measure_unit')

    class Meta:
        model = IngredientForRecipe
        fields = ('id', 'name', 'measure_unit', 'quantity')


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для рецептов"""
    author = CustomUserSerializer()
    ingredients = IngredientForRecipeSerializer(many=True)
    tag = TagSerializer(many=True, read_only=True)
    image = Base64ImageField()
    is_favourite = serializers.SerializerMethodField()
    is_shopping_list = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = '__all__'

    def get_is_favourite(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return Favourite.objects.filter(
            user=request.user, recipe=obj
        ).exists()

    def get_is_shopping_list(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return ShoppingList.objects.filter(
            user=request.user, recipe=obj
        ).exists()


class ShortRecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = ('id', 'name', 'image', 'cooking_time')


class RecipeCreateSerializer(serializers.ModelSerializer):
    tag = TagSerializer(many=True, read_only=True)
    image = Base64ImageField()
    ingredients = IngredientForRecipeSerializer(many=True)

    class Meta:
        model = Recipe
        fields = '__all__'

    def validate(self, data):
        name = str(self.initial_data.get('name')).strip()
        cooking_time = self.initial_data.get('cooking_time')
        if cooking_time < 1:
            raise serializers.ValidationError(
                'Время приготовления должно быть больше 1 минуты!')
        ingredients = self.initial_data.get('ingredients')
        ingredients_set = set()
        for ingredient in ingredients:
            if int(ingredient.get('quantity')) <= 0:
                raise serializers.ValidationError(
                    'Количество ингредиента должно быть больше 0!')
            id = ingredient.get('id')
            if id in ingredients_set:
                raise serializers.ValidationError(
                    'Этот ингредиент вы уже указали!')
            ingredients_set.add(id)
        data['name'] = name.capitalize()
        data['ingredients'] = ingredients
        data['cooking_time'] = cooking_time
        return data

    def create(self, validated_data):
        tag = self.initial_data.get('tag')
        image = validated_data.pop('image')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(
            **validated_data,
            image=image,
            author=self.context.get('request').user
        )
        for tag_id in tag:
            recipe.tag.add(get_object_or_404(Tag, pk=tag_id))
        for ingredient in ingredients:
            ingredient_instance = get_object_or_404(
                Ingredient, pk=ingredient.get('id')
            )
            IngredientForRecipe.objects.create(
                recipe=recipe,
                ingredient=ingredient_instance,
                quantity=ingredient.get('quantity')
            )
        return recipe

    def update(self, recipe, validated_data):
        tag = validated_data.get('tags')
        ingredients = validated_data.get('ingredients')
        recipe.image = validated_data.get(
            'image', recipe.image)
        recipe.name = validated_data.get(
            'name', recipe.name)
        recipe.text = validated_data.get(
            'text', recipe.text)
        recipe.cooking_time = validated_data.get(
            'cooking_time', recipe.cooking_time)
        if tag:
            recipe.tag.clear()
            recipe.tag.set(tag)

        if ingredients:
            recipe.ingredients.clear()
            for ingredient in ingredients:
                ingredient_instance = get_object_or_404(
                    Ingredient, pk=ingredient.get('id')
                )
                IngredientForRecipe.objects.create(
                    recipe=recipe,
                    ingredient=ingredient_instance,
                    quantity=ingredient.get('quantity')
                )

        recipe.save()
        return recipe


class SubscriptionSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    author = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = Subscription
        fields = '__all__'

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
    class Meta:
        model = Favourite
        fields = '__all__'


class ShoppingListSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShoppingList
        fields = '__all__'
