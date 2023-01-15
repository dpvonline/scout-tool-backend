from rest_framework import serializers
from food import models as food_models
from django.contrib.auth.models import User
from food.service.nutri_lib import Nutri

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
    portions = serializers.SerializerMethodField()
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
            'major_class',
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
            'portions'
        )
    
    def get_portions(self, obj):
        jjj = food_models.Portion.objects.filter(ingredient=obj.id)
        return PortionSerializer(jjj, many=True).data


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
    price_per_kg = serializers.SerializerMethodField()
    price = serializers.SerializerMethodField()
        
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
        
    def get_price_per_kg(self, obj):
        portions = food_models.Portion.objects.filter(ingredient=obj.portion.ingredient.id)
        packages = food_models.Package.objects.filter(portion__in=portions)
        data = food_models.Price.objects.filter(package__in=packages)
        sum_value = 0
        count = 0.000000000001
        for item in PriceSerializer(data, many=True).data:
            count = count + 1
            sum_value = sum_value + item.get('price_per_kg')
        return round(sum_value / count, 2)
    
    def get_price(self, obj):
        portions = food_models.Portion.objects.filter(ingredient=obj.portion.ingredient.id)
        packages = food_models.Package.objects.filter(portion__in=portions)
        data = food_models.Price.objects.filter(package__in=packages)
        sum_value = 0
        count = 0.000000000001
        for item in PriceSerializer(data, many=True).data:
            count = count + 1
            sum_value = sum_value + (item.get('price_per_kg') * (obj.weight_g / 1000))
        return round(sum_value / count, 2)


class RecipeSerializer(serializers.ModelSerializer):
    hints = food_serializers.HintSerializer(many=True, required=False)
    tags = food_serializers.TagSerializer(many=True, required=False)
    recipe_items = RecipeItemReadSerializer(many=True, read_only=True)
    price_per_kg = serializers.SerializerMethodField()
    price = serializers.SerializerMethodField()

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
        
    def get_price_per_kg(self, obj):
        data = food_models.RecipeItem.objects.filter(recipe=obj)
        sum_value = 0
        count = 0.000000000001
        for item in RecipeItemReadSerializer(data, many=True).data:
            count = count + 1
            sum_value = sum_value + item.get('price_per_kg')
        return round(sum_value / count, 2)
        
    def get_price(self, obj):
        data = food_models.RecipeItem.objects.filter(recipe=obj)
        sum_value = 0
        count = 0.000000000001
        for item in RecipeItemReadSerializer(data, many=True).data:
            count = count + 1
            sum_value = sum_value + (item.get('price_per_kg') * (obj.weight_g / 1000))
        return round(sum_value / count, 2)

class RecipeDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = food_models.Recipe
        fields = (
            'id',
            'name',
            'nutri_class',
            'nutri_points',
            'weight_g',
            'energy_kj',
            'protein_g',
            'fat_g',
            'fat_sat_g',
            'sugar_g',
            'sodium_mg',
            'salt_g',
        )
class RetailerSerializer(serializers.ModelSerializer):
    class Meta:
        model = food_models.Retailer
        fields = '__all__'

class PhysicalActivityLevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = food_models.PhysicalActivityLevel
        fields = '__all__'


class PackageSerializer(serializers.ModelSerializer):

    price_per_kg = serializers.SerializerMethodField()
    class Meta:
        model = food_models.Package
        fields = (
            'id',
            'name',
            'quality',
            'quantity',
            'weight_package_g',
            'price_per_kg',
        )
        
    def get_price_per_kg(self, obj):
        data = food_models.Price.objects.filter(package=obj)
        sum_value = 0
        count = 0.000000000001
        for item in PriceSerializer(data, many=True).data:
            count = count + 1
            sum_value = sum_value + item.get('price_per_kg')
        return round(sum_value / count, 2)



class PackageReadSerializer(serializers.ModelSerializer):
    price_per_kg = serializers.SerializerMethodField()
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
        
    def get_price_per_kg(self, obj):
        data = food_models.Price.objects.filter(package=obj)
        sum_value = 0
        count = 0.000000000001
        for item in PriceSerializer(data, many=True).data:
            count = count + 1
            sum_value = sum_value + item.get('price_per_kg')
        return round(sum_value / count, 2)

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
    recipe = RecipeDataSerializer(many=False, read_only=True)
    energy_kj = serializers.SerializerMethodField()
    nutri_points = serializers.SerializerMethodField()
    price_eur = serializers.SerializerMethodField()
    weight_g = serializers.SerializerMethodField()
    class Meta:
        model = food_models.MealItem
        fields = (
            'id',
            'recipe',
            'meal',
            'factor',
            'energy_kj',
            'nutri_points',
            'price_eur',
            'weight_g'
        )

    def get_energy_kj(self, obj):
        return round(obj.recipe.energy_kj * obj.factor, 0)

    def get_nutri_points(self, obj):
        return round(obj.recipe.nutri_points * obj.factor, 1)

    def get_price_eur(self, obj):
        return round(obj.recipe.price * obj.factor, 2)

    def get_weight_g(self, obj):
        return round(obj.recipe.weight_g * obj.factor, 0)

class MealItemReadExtendedSerializer(serializers.ModelSerializer):
    recipe = RecipeSerializer(many=False, read_only=True)
    class Meta:
        model = food_models.MealItem
        fields = '__all__'

class MealItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = food_models.MealItem
        fields = '__all__'


class MealReadSerializer(serializers.ModelSerializer):
    meal_items = serializers.SerializerMethodField()
    energy_kj = serializers.SerializerMethodField()
    nutri_points = serializers.SerializerMethodField()
    nutri_class = serializers.SerializerMethodField()
    price_eur = serializers.SerializerMethodField()
    weight_g = serializers.SerializerMethodField()
    day_part_energy_kj = serializers.SerializerMethodField()
    class Meta:
        model = food_models.Meal
        fields = (
            "id",
            'name',
            'meal_day',
            'day_part_factor',
            'meal_type',
            'get_meal_type_display',
            'meal_items',
            'energy_kj',
            'nutri_points',
            'price_eur',
            'weight_g',
            'nutri_class',
            'day_part_energy_kj'
        )
        
    def get_meal_items(self, obj):
        jjj = food_models.MealItem.objects.filter(meal=obj)
        return MealItemReadSerializer(jjj, many=True).data
    
    def get_energy_kj(self, obj):
        jjj = food_models.MealItem.objects.filter(meal=obj)
        sum_value = 0
        for item in MealItemReadSerializer(jjj, many=True).data:
            sum_value = sum_value + item.get('energy_kj')
        return round(sum_value, 0)
    
    def get_day_part_energy_kj(self, obj):
        jjj = food_models.MealItem.objects.filter(meal=obj)
        sum_value = 0
        for item in MealItemReadSerializer(jjj, many=True).data:
            sum_value = sum_value + item.get('energy_kj')
        return obj.day_part_factor and round( sum_value / (11500 * obj.day_part_factor), 2)

    def get_price_eur(self, obj):
        data = food_models.MealItem.objects.filter(meal=obj)
        sum_value = 0
        for item in MealItemReadSerializer(data, many=True).data:
            sum_value = sum_value + item.get('price_eur')
        return round(sum_value, 2)
    
    def get_weight_g(self, obj):
        data = food_models.MealItem.objects.filter(meal=obj)
        sum_value = 0
        for item in MealItemReadSerializer(data, many=True).data:
            sum_value = sum_value + item.get('weight_g')
        return round(sum_value, 0)
    
    def get_nutri_points(self, obj):
        data = food_models.MealItem.objects.filter(meal=obj)
        sum_value = 0
        sum_weight = 0.001
        for item in MealItemReadSerializer(data, many=True).data:
            sum_value = sum_value + item.get('nutri_points') * item.get('weight_g')
            sum_weight = sum_weight + item.get('weight_g')
        return round(sum_value / sum_weight, 1)
    
    def get_nutri_class(self, obj):
        NutriClass = Nutri()
        data = food_models.MealItem.objects.filter(meal=obj)
        sum_value = 0
        sum_weight = 0.001
        for item in MealItemReadSerializer(data, many=True).data:
            sum_value = sum_value + item.get('nutri_points') * item.get('weight_g')
            sum_weight = sum_weight + item.get('weight_g')
            
        nutri_class = NutriClass.get_nutri_class(
            'solid', sum_value/sum_weight)
        return round(nutri_class, 2)
    
class MealReadExtendedSerializer(serializers.ModelSerializer):
    meal_items = serializers.SerializerMethodField()
    class Meta:
        model = food_models.Meal
        fields = '__all__'
        
    def get_meal_items(self, obj):
        jjj = food_models.MealItem.objects.filter(meal=obj)
        return MealItemReadExtendedSerializer(jjj, many=True).data

class MealSerializer(serializers.ModelSerializer):
    class Meta:
        model = food_models.Meal
        fields = '__all__'

class MealDayReadSerializer(serializers.ModelSerializer):
    meals = serializers.SerializerMethodField()
    energy_kj = serializers.SerializerMethodField()
    price_eur = serializers.SerializerMethodField()
    weight_g = serializers.SerializerMethodField()
    nutri_points = serializers.SerializerMethodField()
    nutri_class = serializers.SerializerMethodField()
    day_factors = serializers.SerializerMethodField()
    class Meta:
        model = food_models.MealDay
        fields = '__all__'
        
    def get_meals(self, obj):
        data = food_models.Meal.objects.filter(meal_day=obj)
        return MealReadSerializer(data, many=True).data
    
    def get_energy_kj(self, obj):
        jjj = food_models.Meal.objects.filter(meal_day=obj)
        sum_energy_kj = 0
        for item in MealReadSerializer(jjj, many=True).data:
            sum_energy_kj = sum_energy_kj + item.get('energy_kj')
        return round(sum_energy_kj, 0)
    
    def get_price_eur(self, obj):
        data = food_models.Meal.objects.filter(meal_day=obj)
        sum_value = 0
        for item in MealReadSerializer(data, many=True).data:
            sum_value = sum_value + item.get('price_eur')
        return round(sum_value, 2)
    
    def get_weight_g(self, obj):
        data = food_models.Meal.objects.filter(meal_day=obj)
        sum_value = 0
        for item in MealReadSerializer(data, many=True).data:
            sum_value = sum_value + item.get('weight_g')
        return round(sum_value, 0)
    
    def get_nutri_points(self, obj):
        data = food_models.Meal.objects.filter(meal_day=obj)
        sum_value = 0
        for item in MealReadSerializer(data, many=True).data:
            sum_value = sum_value + item.get('nutri_points') * item.get('day_part_factor')
        return round(sum_value, 1)
    
    def get_day_factors(self, obj):
        data = food_models.Meal.objects.filter(meal_day=obj)
        sum_value = 0
        for item in MealReadSerializer(data, many=True).data:
            sum_value = sum_value + item.get('day_part_factor')
        return round(sum_value, 2)
    
    def get_nutri_class(self, obj):
        NutriClass = Nutri()
        data = food_models.Meal.objects.filter(meal_day=obj)
        sum_value = 0
        for item in MealReadSerializer(data, many=True).data:
            sum_value = sum_value + item.get('nutri_points') * item.get('day_part_factor')
        nutri_class = NutriClass.get_nutri_class(
            'solid', sum_value)
        return nutri_class

class MealDayReadExtendedSerializer(serializers.ModelSerializer):
    meals = serializers.SerializerMethodField()
    class Meta:
        model = food_models.MealDay
        fields = '__all__'
        
    def get_meals(self, obj):
        data = food_models.Meal.objects.filter(meal_day=obj)
        return MealReadExtendedSerializer(data, many=True).data


class MealDaySerializer(serializers.ModelSerializer):
    class Meta:
        model = food_models.MealDay
        fields = '__all__'

class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = food_models.Event
        fields = '__all__'

class EventReadSerializer(serializers.ModelSerializer):
    meal_days = serializers.SerializerMethodField()
    energy_kj = serializers.SerializerMethodField()
    price_eur = serializers.SerializerMethodField()
    weight_g = serializers.SerializerMethodField()
    nutri_points = serializers.SerializerMethodField()
    nutri_class = serializers.SerializerMethodField()
    class Meta:
        model = food_models.Event
        fields = '__all__'
        
    def get_meal_days(self, obj):
        jjj = food_models.MealDay.objects.filter(event=obj)
        return MealDayReadSerializer(jjj, many=True).data
    
    def get_energy_kj(self, obj):
        jjj = food_models.MealDay.objects.filter(event=obj)
        sum_energy_kj = 0
        for item in MealDayReadSerializer(jjj, many=True).data:
            sum_energy_kj = sum_energy_kj + item.get('energy_kj')
        return round(sum_energy_kj, 0)
    
    def get_price_eur(self, obj):
        data = food_models.MealDay.objects.filter(event=obj)
        sum_value = 0
        for item in MealDayReadSerializer(data, many=True).data:
            sum_value = sum_value + item.get('price_eur')
        return round(sum_value, 2)
    
    def get_weight_g(self, obj):
        data = food_models.MealDay.objects.filter(event=obj)
        sum_value = 0
        for item in MealDayReadSerializer(data, many=True).data:
            sum_value = sum_value + item.get('weight_g')
        return round(sum_value, 0)
    
    def get_nutri_points(self, obj):
        data = food_models.MealDay.objects.filter(event=obj)
        sum_value = 0
        for item in MealDayReadSerializer(data, many=True).data:
            sum_value = sum_value + item.get('nutri_points')
        return round(sum_value, 1)
    
    def get_day_factors(self, obj):
        data = food_models.Meal.objects.filter(meal_day=obj)
        sum_value = 0
        for item in MealReadSerializer(data, many=True).data:
            sum_value = sum_value + item.get('day_part_factor')
        return round(sum_value, 2)
    
    def get_nutri_class(self, obj):
        NutriClass = Nutri()
        data = food_models.MealDay.objects.filter(event=obj)
        sum_value = 0
        for item in MealDayReadSerializer(data, many=True).data:
            sum_value = sum_value + item.get('nutri_points')
            
        nutri_class = NutriClass.get_nutri_class(
            'solid', sum_value)
        return nutri_class

class EventReadExtendedSerializer(serializers.ModelSerializer):
    meal_days = serializers.SerializerMethodField()
    class Meta:
        model = food_models.Event
        fields = '__all__'
        
    def get_meal_days(self, obj):
        jjj = food_models.MealDay.objects.filter(event=obj)
        return MealDayReadExtendedSerializer(jjj, many=True).data

