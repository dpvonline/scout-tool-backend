from django.db.models import Q, QuerySet
from django_filters import CharFilter, NumberFilter
from django_filters.rest_framework import DjangoFilterBackend, FilterSet
from rest_framework import viewsets, status
from rest_framework.exceptions import PermissionDenied, NotFound
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from copy import deepcopy

from food import models as food_models
from food import serializers as food_serializers


class MeasuringUnitViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = food_models.MeasuringUnit.objects.all()
    serializer_class = food_serializers.MeasuringUnitSerializer


class HintViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = food_models.Hint.objects.all()
    serializer_class = food_serializers.HintSerializer


class PriceReadViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = food_models.Price.objects.all()
    serializer_class = food_serializers.PriceReadSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['id', 'package__portion__ingredient__id']


class PriceViewSet(viewsets.ModelViewSet):
    queryset = food_models.Price.objects.all()
    serializer_class = food_serializers.PriceSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['id', 'package__portion__ingredient__id']
    
    def create(self, request, *args, **kwargs) -> Response:
        request.data['retailer'] = request.data['retailer']['id']
        if isinstance(request.data['package'], object) and request.data['package']:
            request.data['package'] = request.data['package']['id']
        else:
            new_package = food_models.Package.objects.create(
                name = request.data['name'],
                portion = get_object_or_404(food_models.Portion , id = request.data['portion']['id']),
                quantity = request.data['quantity'],
                quality = request.data['quality'],
                
            )
            request.data['package'] = new_package.id
        
        print(request.data)
        return super().create(request, *args, **kwargs)


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

class RecipeCloneViewSet(viewsets.ViewSet):
    def create(self, request, *args, **kwargs) -> Response:
        if request.data.get('id', None) is not None:
            recipe_id = request.data.get('id')
            old_recipe_obj = food_models.Recipe.objects.filter(id=request.data.get('id')).first()
            new_old_obj = deepcopy(old_recipe_obj)
            new_old_obj.id = None
            new_old_obj.status = 'simulator'
            new_old_obj.save()
            
            all_items = food_models.RecipeItem.objects.filter(recipe=recipe_id)
            
            for item in all_items:
                new = deepcopy(item)
                new.recipe = new_old_obj
                new.save()
            return Response(food_serializers.RecipeSerializer(new_old_obj).data, status=status.HTTP_201_CREATED)
        
        return Response({ 'Bitte ID mitgeben'}, status=status.HTTP_400_BAD_REQUEST)

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


class RetailerViewSet(viewsets.ModelViewSet):
    queryset = food_models.Retailer.objects.all()
    serializer_class = food_serializers.RetailerSerializer


class PackageViewSet(viewsets.ModelViewSet):
    queryset = food_models.Package.objects.all()
    serializer_class = food_serializers.PackageSerializer


class PackageReadViewSet(viewsets.ModelViewSet):
    queryset = food_models.Package.objects.all()
    serializer_class = food_serializers.PackageReadSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['portion__ingredient__id']


class PortionViewSet(viewsets.ModelViewSet):
    queryset = food_models.Portion.objects.all().order_by('rank').order_by('name')
    serializer_class = food_serializers.PortionSerializer
    def create(self, request, *args, **kwargs) -> Response:
        request.data['measuring_unit'] = request.data['measuring_unit']['id']
        
        return super().create(request, *args, **kwargs)
    



class PortionReadViewSet(viewsets.ModelViewSet):
    queryset = food_models.Portion.objects.all().order_by('rank').order_by('name')
    serializer_class = food_serializers.PortionReadSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['id', 'name', 'ingredient__id']
    search_fields = ['name', 'ingredient__name']
