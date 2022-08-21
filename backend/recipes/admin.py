from django.contrib import admin

from . import models


class IngredientRecipe(admin.TabularInline):
    model = models.IngredientForRecipe
    min_num = 1
    extra = 1


@admin.register(models.Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'measure_unit')
    search_fields = ('name',)
    list_filter = ('name',)


@admin.register(models.Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'author')
    list_filter = ('name', 'author', 'tags')
    readonly_fields = ['added_to_favorites']
    inlines = [IngredientRecipe]

    def added_to_favorites(self, obj):
        return obj.favorite.count()
    added_to_favorites.short_description = 'Добавили в избранное'

@admin.register(models.Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'colour')
