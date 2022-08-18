from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from recipes.models import (Favourite, Ingredient, IngredientForRecipe, Recipe,
                            ShoppingList, Tag)
from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from users.models import Subscription

from .pagination import PagePagination
from .permissions import IsAdminOrReadOnly, IsAuthorOrAdminOrReadOnly
from .serializers import (CustomUserSerializer, FavouriteSerializer,
                          IngredientSerializer, RecipeCreateSerializer,
                          RecipeSerializer, ShoppingListSerializer,
                          SubscriptionSerializer, TagSerializer)

User = get_user_model()


class CustomUserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    pagination_class = PagePagination

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated])
    def subscribe(self, request, id=None):
        user = get_object_or_404(User, username=request.user.username)
        author = get_object_or_404(User, id=id)
        if request.method == 'POST':
            if user == author:
                return Response({
                    'errors': 'Нельзя подписаться на себя'
                }, status=status.HTTP_400_BAD_REQUEST)
            if Subscription.objects.filter(user=user, author=author).exists():
                return Response({
                    'errors': 'Вы уже подписались на этого пользователя'
                }, status=status.HTTP_400_BAD_REQUEST)
            subscription = Subscription.objects.create(
                user=user,
                author=author)
            serializer = SubscriptionSerializer(
                subscription,
                context={"request": request},
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == "DELETE":
            subscription = Subscription.objects.filter(
                user=user,
                author=author,
            )
            if subscription.exists():
                subscription.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response({
                    'errors': 'Вы не подписаны на этого автора'
                }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, permission_classes=[IsAuthenticated])
    def subscriptions(self, request):
        user = request.user
        queryset = Subscription.objects.filter(user=user)
        pages = self.paginate_queryset(queryset)
        serializer = SubscriptionSerializer(
            pages,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAdminOrReadOnly,)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    permission_classes = (IsAdminOrReadOnly,)
    search_fields = ('^name',)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeSerializer
        return RecipeCreateSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        instance = serializer.instance
        out_serializer = RecipeSerializer(
            instance=instance, context={"request": request}
        )
        return Response(
            out_serializer.data, status=status.HTTP_201_CREATED
        )

    def get_permissions(self):
        if (self.action == 'list' or self.action == 'retrieve'
                or self.action == 'create'):
            permission_classes = [permissions.IsAuthenticatedOrReadOnly]
        else:
            permission_classes = [IsAuthorOrAdminOrReadOnly]
        return [permission() for permission in permission_classes]

    @action(detail=True, methods=['post'],
            permission_classes=[IsAuthenticated])
    def favorite(self, request, pk=None):
        data = {'user': request.user.id, 'recipe': pk}
        serializer = FavouriteSerializer(
            data=data,
            context={'request': request})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @favorite.mapping.delete
    def favorite_delete(self, request, pk=None):
        user = request.user
        recipe = get_object_or_404(Recipe, id=pk)
        favourite_check = Favourite.objects.filter(
            user=user, recipe=recipe).exists()
        if not favourite_check:
            return Response(
                {'error': 'Этого рецепта нет в избранных'},
                status=status.HTTP_400_BAD_REQUEST
            )
        favourite = get_object_or_404(Favourite, user=user, recipe=recipe)
        favourite.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post'],
            permission_classes=[IsAuthenticated])
    def shopping_cart(self, request, pk=None):
        data = {'user': request.user.id, 'recipe': pk}
        serializer = ShoppingListSerializer(
            data=data,
            context={'request': request})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @shopping_cart.mapping.delete
    def shopping_cart_delete(self, request, pk=None):
        user = request.user
        recipe = get_object_or_404(Recipe, id=pk)
        check_list = ShoppingList.objects.filter(
            user=user, recipe=recipe).exists()
        if not check_list:
            return Response(
                {'error': 'Этого рецепта нет в списке покупок'},
                status=status.HTTP_400_BAD_REQUEST
            )
        shopping_list = get_object_or_404(
            ShoppingList, user=user, recipe=recipe)
        shopping_list.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False,
            methods=['GET'],
            permission_classes=[IsAuthenticated])
    def download_shopping_cart(self, request):
        all_ingredients = IngredientForRecipe.objects.filter(
            recipe__shopping_list__user=request.user)
        ingredients_total = {}
        for ingredient in all_ingredients:
            name = ingredient.ingredient.name
            amount = ingredient.amount
            measure_unit = ingredient.ingredient.measure_unit
            if name in ingredients_total:
                ingredients_total[name]['amount'] += amount
                amount = ingredients_total[name]['amount']
            ingredients_total[name] = {
                'measurement_unit': measure_unit,
                'amount': amount
            }
        shopping_list = []
        num = 1
        for ingredient in ingredients_total:
            shopping_list.append(
                f'{num}. {ingredient} - '
                f'{ingredients_total[ingredient]["amount"]} '
                f'{ingredients_total[ingredient]["measurement_unit"]} \n'
            )
            num += 1
        filename = 'shopping_list.txt'
        response = HttpResponse(shopping_list, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename={filename}'
        return response
