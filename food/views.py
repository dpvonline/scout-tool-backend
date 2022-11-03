from django.db.models import Q, QuerySet
from django_filters import CharFilter, NumberFilter
from django_filters.rest_framework import DjangoFilterBackend, FilterSet
from rest_framework import viewsets, status
from rest_framework.exceptions import PermissionDenied, NotFound
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from food import models as food_models
from food import serializers as food_serializers


class MeasuringUnitViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = food_models.MeasuringUnit.objects.all()
    serializer_class = food_serializers.MeasuringUnitSerializer


class PriceViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = food_models.Price.objects.all()
    serializer_class = food_serializers.PriceSerializer


class TagCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = food_models.TagCategory.objects.all()
    serializer_class = food_serializers.TagCategorySerializer


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = food_models.Tag.objects.all()
    serializer_class = food_serializers.TagSerializer


class IngredientFilter(FilterSet):
    nutri_class = NumberFilter(field_name='nutri_class')
    physical_viscosity = CharFilter(field_name='physical_viscosity')

class IngredientViewSet(viewsets.ModelViewSet):
    queryset = food_models.Ingredient.objects.all()
    serializer_class = food_serializers.IngredientSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = IngredientFilter
    ordering = ['name']
    ordering_fields = ['name', 'created_at', 'nutri_points']
    filterset_fields = ['name']
    search_fields = ['name']


class RecipeItemViewSet(viewsets.ModelViewSet):
    queryset = food_models.RecipeItem.objects.all()
    serializer_class = food_serializers.RecipeItemSerializer


class RecipeFilter(FilterSet):
    nutri_class = NumberFilter(field_name='nutri_class')
    physical_viscosity = CharFilter(field_name='physical_viscosity')

class RecipeViewSet(viewsets.ModelViewSet):
    queryset = food_models.Recipe.objects.all()
    serializer_class = food_serializers.RecipeSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = RecipeFilter
    ordering = ['name']
    ordering_fields = ['name', 'created_at', 'nutri_points']
    filterset_fields = ['name']
    search_fields = ['name']
    
class RecipeReadViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = food_models.Recipe.objects.all()
    serializer_class = food_serializers.RecipeSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = RecipeFilter
    ordering = ['name']
    ordering_fields = ['name', 'created_at', 'nutri_points']
    filterset_fields = ['name']
    search_fields = ['name']
    def get_queryset(self) -> QuerySet:
        return food_models.Recipe.objects.filter(status="verified")


class RetailerViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = food_models.Retailer.objects.all()
    serializer_class = food_serializers.RetailerSerializer


class PackageViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = food_models.Package.objects.all()
    serializer_class = food_serializers.PackageSerializer


class PortionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = food_models.Portion.objects.all().order_by('rank').order_by('name')
    serializer_class = food_serializers.PortionSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['id', 'name', 'ingredient__id']
    search_fields = ['name', 'ingredient__name']
