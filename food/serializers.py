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
        fields = (
            'carbohydrate_g',
            'created_at',
            'description',
            'energy_kj',
            'fat_g',
            'fat_sat_g',
            'fdc_id',
            'fibre_g',
            'fructose_g',
            'fruit_factor',
            'id',
            'lactose_g',
            'get_major_class_display',
            'name',
            'ndb_number',
            'nutri_class',
            'nutri_points',
            'nutri_points_energy_kj',
            'nutri_points_fat_sat_g',
            'nutri_points_fibre_g',
            'nutri_points_protein_g',
            'nutri_points_salt_g',
            'nutri_points_sodium_mg',
            'nutri_points_sugar_g',
            'physical_density',
            'physical_viscosity',
            'protein_g',
            'salt_g',
            'sodium_mg',
            'sugar_g',
            'tags',
            'updated_at',
            'price_per_kg',
        )


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
            'get_meal_type_display',
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
    portion = PortionReadSerializer(many=False, read_only=True)
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

class MealItemReadSerializer(serializers.ModelSerializer):
    recipe = RecipeSerializer(many=False, read_only=True)
    energy_kj = serializers.SerializerMethodField()
    class Meta:
        model = food_models.MealItem
        fields = (
            'id',
            'recipe',
            'meal',
            'factor',
            'energy_kj'
        )

    def get_energy_kj(self, obj):
        return round(obj.recipe.energy_kj * obj.factor, 0)

class MealItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = food_models.MealItem
        fields = '__all__'


class MealReadSerializer(serializers.ModelSerializer):
    meal_items = serializers.SerializerMethodField()
    energy_kj = serializers.SerializerMethodField()
    class Meta:
        model = food_models.Meal
        fields = (
            "id",
            'name',
            'meal_day',
            'factor',
            'meal_type',
            'get_meal_type_display',
            'meal_items',
            'energy_kj'
        )
        
    def get_meal_items(self, obj):
        jjj = food_models.MealItem.objects.filter(meal=obj)
        return MealItemReadSerializer(jjj, many=True).data
    
    def get_energy_kj(self, obj):
        jjj = food_models.MealItem.objects.filter(meal=obj)
        sum_energy_kj = 0
        for item in MealItemReadSerializer(jjj, many=True).data:
            sum_energy_kj = sum_energy_kj + item.get('energy_kj')
        return round(sum_energy_kj, 0)

class MealSerializer(serializers.ModelSerializer):
    class Meta:
        model = food_models.Meal
        fields = '__all__'


class MealDayReadSerializer(serializers.ModelSerializer):
    meals = serializers.SerializerMethodField()
    energy_kj = serializers.SerializerMethodField()
    class Meta:
        model = food_models.MealDay
        fields = '__all__'
        
    def get_meals(self, obj):
        jjj = food_models.Meal.objects.filter(meal_day=obj)
        return MealReadSerializer(jjj, many=True).data
    
    def get_energy_kj(self, obj):
        jjj = food_models.Meal.objects.filter(meal_day=obj)
        sum_energy_kj = 0
        for item in MealReadSerializer(jjj, many=True).data:
            sum_energy_kj = sum_energy_kj + item.get('energy_kj')
        return round(sum_energy_kj, 0)


class MealDaySerializer(serializers.ModelSerializer):
    class Meta:
        model = food_models.MealDay
        fields = '__all__'

class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = food_models.Event
        fields = (
            'id',
            'name',
            'norm_portions'
        )

class EventReadSerializer(serializers.ModelSerializer):
    meal_days = serializers.SerializerMethodField()
    class Meta:
        model = food_models.Event
        fields = (
            'id',
            'name',
            'norm_portions',
            'meal_days'
        )
        
    def get_meal_days(self, obj):
        jjj = food_models.MealDay.objects.filter(event=obj)
        return MealDayReadSerializer(jjj, many=True).data
