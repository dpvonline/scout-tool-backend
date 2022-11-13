from rest_framework import serializers
from food import models as food_models
from django.contrib.auth.models import User

from food import serializers as food_serializers


class MeasuringUnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = food_models.MeasuringUnit
        fields = '__all__'



class HintSerializer(serializers.ModelSerializer):
    class Meta:
        model = food_models.Hint
        fields = '__all__'


class TagCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = food_models.TagCategory
        fields = '__all__'


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = food_models.Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = food_models.Ingredient
        fields = '__all__'


class PortionReadSerializer(serializers.ModelSerializer):
    ingredient = food_serializers.IngredientSerializer()
    measuring_unit = food_serializers.MeasuringUnitSerializer()
    class Meta:
        model = food_models.Portion
        fields = '__all__'
        
class PortionSerializer(serializers.ModelSerializer):
    class Meta:
        model = food_models.Portion
        fields = '__all__'
        

class RecipeItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = food_models.RecipeItem
        fields = '__all__'

class RecipeItemReadSerializer(serializers.ModelSerializer):
    portion = PortionReadSerializer(many=False, read_only=True)
    class Meta:
        model = food_models.RecipeItem
        fields = (
            'id',
            'nutri_class',
            'nutri_points',
            'weight_g',
            'price_per_kg',
            'price',
            'quantity',
            'portion',
            'energy_kj',
            'protein_g',
            'fat_g',
            'fat_sat_g',
            'sugar_g',
            'sodium_mg',
            'salt_g',
            'fruit_factor',
            'carbohydrate_g',
            'fibre_g',
            'fructose_g',
            'lactose_g',
            'nutri_points_energy_kj',
            'nutri_points_protein_g',
            'nutri_points_fat_sat_g',
            'nutri_points_sugar_g',
            'nutri_points_salt_g',
            'nutri_points_fibre_g',
            'created_at',
            'updated_at',
        )


class RecipeSerializer(serializers.ModelSerializer):
    hints = food_serializers.HintSerializer(many=True, required=False)
    tags = food_serializers.TagSerializer(many=True, required=False)
    recipe_items = RecipeItemReadSerializer(many=True, read_only=True)

    class Meta:
        model = food_models.Recipe
        fields = (
            'id',
            'name',
            'description',
            'tags',
            'meal_type',
            'nutri_class',
            'nutri_points',
            'weight_g',
            'hints',
            'price_per_kg',
            'price',
            'recipe_items',
            'tags',
            'hints',
            'energy_kj',
            'protein_g',
            'fat_g',
            'fat_sat_g',
            'sugar_g',
            'sodium_mg',
            'salt_g',
            'fruit_factor',
            'carbohydrate_g',
            'fibre_g',
            'fructose_g',
            'lactose_g',
            'status',
            'created_at',
            'updated_at',
        )

class RetailerSerializer(serializers.ModelSerializer):
    class Meta:
        model = food_models.Retailer
        fields = '__all__'


class PackageSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = food_models.Package
        fields = (
            'id',
            'name',
            'portion',
            'quality',
            'quantity',
            'weight_package_g',
            'price_per_kg',
        )


class PackageReadSerializer(serializers.ModelSerializer):
    portion = PortionSerializer(many=False, read_only=True)
    class Meta:
        model = food_models.Package
        fields = (
            'id',
            'name',
            'portion',
            'quality',
            'quantity',
            'weight_package_g',
            'price_per_kg',
        )

class PriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = food_models.Price
        fields = (
            'id',
            'price_eur',
            'retailer',
            'package',
            'price_per_kg'
        )
class PriceReadSerializer(serializers.ModelSerializer):
    package = PackageSerializer(many=False, read_only=True)
    retailer = RetailerSerializer(many=False, read_only=True)
    class Meta:
        model = food_models.Price
        fields = (
            'id',
            'price_eur',
            'retailer',
            'package',
            'price_per_kg'
        )
