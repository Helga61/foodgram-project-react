from django.contrib.auth import get_user_model
from django_filters.rest_framework import FilterSet, filters

from recipes.models import Recipe

User = get_user_model()


class NameSearchFilter(filters.SearchFilter):
    search_param = 'name'


class RecipeFilter(FilterSet):
    tags = filters.AllValuesMultipleFilter(field_name='tags__slug')
    author = filters.ModelChoiceFilter(queryset=User.objects.all())
    is_favourite = filters.BooleanFilter(method='filter_is_favorited')
    is_shopping_list = filters.BooleanFilter(method='filter_is_shopping_list')

    class Meta:
        model = Recipe
        fields = ('tags', 'author')

    def filter_is_favorited(self, queryset, name, value):
        if value and not self.request.user.is_anonymous:
            return queryset.filter(favorite__user=self.request.user)
        return queryset

    def filter_is_shopping_list(self, queryset, name, value):
        if value and not self.request.user.is_anonymous:
            return Recipe.objects.filter(shopping_list__user=self.request.user)
        return queryset
