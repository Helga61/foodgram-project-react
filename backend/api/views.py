from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from recipes.models import Favourite, Ingredient, Recipe, ShoppingList, Tag
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from users.models import Subscription

from .pagination import PagePagination
from .permissions import IsAdminOrReadOnly, IsAuthorOrReadOnly
from .serializers import (CustomUserSerializer, IngredientSerializer,
                          RecipeCreateSerializer, RecipeSerializer,
                          ShortRecipeSerializer, SubscriptionSerializer,
                          TagSerializer)

User = get_user_model()


class CustomUserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    pagination_class = PagePagination

    @action(
        detail=True,
        methods=['get', 'delete'],
        permission_classes=[IsAuthenticated])
    def subscribe(self, request, id=None):
        user = get_object_or_404(User, username=request.user.username)
        author = get_object_or_404(User, id=id)
        if request.method == 'get':
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
    filter_backends = (DjangoFilterBackend,)
    permission_classes = (IsAdminOrReadOnly,)
    search_fields = ('^name',)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()

    def get_serializer_class(self):
        if self.request.method in permissions.SAFE_METHODS:
            return RecipeSerializer
        return RecipeCreateSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def perform_update(self, serializer):
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

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = self.get_object()
        self.perform_update(serializer)
        serializer = self.get_serializer(
            instance=instance,
            data=request.data
        )
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        instance = serializer.instance
        out_serializer = RecipeSerializer(
            instance=instance, context={"request": request}
        )
        return Response(out_serializer.data, status=status.HTTP_200_OK)

    def get_permissions(self):
        if (self.action == 'list' or self.action == 'retrieve'
                or self.action == 'create'):
            permission_classes = [permissions.IsAuthenticatedOrReadOnly]
        else:
            permission_classes = [IsAuthorOrReadOnly]
        return [permission() for permission in permission_classes]

    def post_or_delete(self, request, model, error_data):
        user = request.user
        recipe = self.get_object()
        if request.method == "POST":
            if model.objects.filter(
                user=user,
                recipe=recipe
            ).exists():
                return Response(error_data, status=status.HTTP_400_BAD_REQUEST)
            model.objects.create(
                user=user,
                recipe=recipe,
            )
            serializer = ShortRecipeSerializer(
                recipe,
                context={"request": request},
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        action_object = model.objects.filter(
            user=user,
            recipe=recipe,
        )
        if action_object.exists():
            action_object.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(error_data, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=[IsAuthenticated])
    def favorite(self, request, **kwargs):
        if request.method == "POST":
            model = Favourite
            error_data = {"errors": "Рецепт уже добавлен в избранное"}
            return self.post_or_delete(request, model, error_data)
        if request.method == "DELETE":
            model = Favourite
            error_data = {"errors": "Рецепт уже удален из избранного"}
            return self.post_or_delete(request, model, error_data)
        return None

    @action(detail=True, methods=["post", "delete"])
    def shopping_list(self, request, **kwargs):
        if request.method == "POST":
            model = ShoppingList
            error_data = {"errors": "Рецепт уже добавлен в список покупок"}
            return self.post_or_delete(request, model, error_data)
        if request.method == "DELETE":
            model = ShoppingList
            error_data = {"errors": "Рецепт уже удален из списка покупок"}
            return self.post_or_delete(request, model, error_data)
        return None
