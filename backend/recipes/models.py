from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

User = get_user_model()


class Tag(models.Model):
    name = models.CharField('Тег', max_length=20, unique=True)
    color = models.CharField(
        'Цвет в Hex',
        max_length=10
    )
    slug = models.SlugField('Идентификатор', unique=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField('Ингредиент', max_length=200)
    measure_unit = models.CharField(
        'Единицы измерения', max_length=15)

    class Meta:
        ordering = ['pk']
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор'
    )
    name = models.CharField('Название', max_length=200)
    image = models.ImageField(
        'Изображение',
        upload_to='recipe/images',
        blank=True
    )
    text = models.TextField(
        'Рецепт',
        help_text='Опишите процесс приготовления'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientForRecipe',
        related_name='recipes',
        verbose_name='Ингредиенты'
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='Теги'
    )
    cooking_time = models.PositiveSmallIntegerField(
        validators=(MinValueValidator(
            1,
            message='Время приготовления должно быть не меньше 1 минуты!'),),
        verbose_name='Время приготовления в минутах'
    )
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True)

    class Meta:
        ordering = ['-pub_date']
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name[:25]


class IngredientForRecipe(models.Model):
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='ingredient_for_recipe',
        verbose_name='Ингредиент'
    )
    amount = models.PositiveSmallIntegerField('Количество')
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='ingredient_for_recipe',
        verbose_name='Рецепт'
    )

    class Meta:
        ordering = ['ingredient']
        verbose_name = 'Ингредиенты для рецепта'
        verbose_name_plural = 'Ингредиенты для рецептов'
        constraints = [
            models.UniqueConstraint(
                fields=['ingredient', 'recipe'],
                name='ingredient_for_recipe_unique'
            ),
        ]

    def __str__(self):
        return f'{self.ingredient}: {self.amount}'


class Favourite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorite',
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorite',
        verbose_name='Рецепт'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='favourite_unique'
            ),
        ]
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'


class ShoppingList(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_list',
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shopping_list',
        verbose_name='Рецепт'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='shopping_list_unique'
            ),
        ]
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'

    def __str__(self):
        return f'Список покупок {self.user.username}'
