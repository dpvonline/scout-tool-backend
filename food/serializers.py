from rest_framework import serializers
from food import models as food_models
from django.contrib.auth.models import User
from food.service.nutri_lib import Nutri
from rest_framework.fields import CurrentUserDefault
from food.service.agg_lib import AggLib
from keycloak_auth.helper import get_groups_of_user
from keycloak_auth.models import KeycloakGroup

from food import serializers as food_serializers
from anmelde_tool.event import serializers as event_serializers
from anmelde_tool.registration import serializers as registration_serializers


class MeasuringUnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = food_models.MeasuringUnit
        fields = "__all__"


class HintSerializer(serializers.ModelSerializer):
    class Meta:
        model = food_models.Hint
        fields = "__all__"


class TagCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = food_models.TagCategory
        fields = "__all__"


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = food_models.Tag
        fields = "__all__"


class IngredientSerializer(serializers.ModelSerializer):
    portions = serializers.SerializerMethodField()

    class Meta:
        model = food_models.Ingredient
        fields = (
            "carbohydrate_g",
            "created_at",
            "description",
            "energy_kj",
            "fat_g",
            "fat_sat_g",
            "fdc_id",
            "fibre_g",
            "fructose_g",
            "fruit_factor",
            "id",
            "lactose_g",
            "major_class",
            "get_major_class_display",
            "name",
            "ndb_number",
            "nutri_class",
            "nutri_points",
            "nutri_points_energy_kj",
            "nutri_points_fat_sat_g",
            "nutri_points_fibre_g",
            "nutri_points_protein_g",
            "nutri_points_salt_g",
            "nutri_points_sodium_mg",
            "nutri_points_sugar_g",
            "physical_density",
            "physical_viscosity",
            "protein_g",
            "salt_g",
            "sodium_mg",
            "sugar_g",
            "tags",
            "updated_at",
            "portions",
        )

    def get_portions(self, obj):
        jjj = food_models.Portion.objects.filter(ingredient=obj.id)
        return PortionSerializer(jjj, many=True).data


class PortionReadSerializer(serializers.ModelSerializer):
    ingredient = food_serializers.IngredientSerializer()
    measuring_unit = food_serializers.MeasuringUnitSerializer()

    class Meta:
        model = food_models.Portion
        fields = "__all__"


class PortionSerializer(serializers.ModelSerializer):
    class Meta:
        model = food_models.Portion
        fields = "__all__"


class RecipeItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = food_models.RecipeItem
        fields = "__all__"


class RecipeItemReadSerializer(serializers.ModelSerializer):
    portion = PortionReadSerializer(many=False, read_only=True)
    price_per_kg = serializers.SerializerMethodField()
    price = serializers.SerializerMethodField()

    class Meta:
        model = food_models.RecipeItem
        fields = (
            "id",
            "nutri_class",
            "nutri_points",
            "weight_g",
            "price_per_kg",
            "price",
            "quantity",
            "portion",
            "energy_kj",
            "protein_g",
            "fat_g",
            "fat_sat_g",
            "sugar_g",
            "sodium_mg",
            "salt_g",
            "fruit_factor",
            "carbohydrate_g",
            "fibre_g",
            "fructose_g",
            "lactose_g",
            "nutri_points_energy_kj",
            "nutri_points_protein_g",
            "nutri_points_fat_sat_g",
            "nutri_points_sugar_g",
            "nutri_points_salt_g",
            "nutri_points_fibre_g",
            "created_at",
            "updated_at",
        )

    def get_price_per_kg(self, obj):
        portions = food_models.Portion.objects.filter(
            ingredient=obj.portion.ingredient.id
        )
        packages = food_models.Package.objects.filter(portion__in=portions)
        data = food_models.Price.objects.filter(package__in=packages)
        sum_value = 0
        count = 0.000000000001
        for item in PriceSerializer(data, many=True).data:
            count = count + 1
            sum_value = sum_value + item.get("price_per_kg")
        return round(sum_value / count, 2)

    def get_price(self, obj):
        portions = food_models.Portion.objects.filter(
            ingredient=obj.portion.ingredient.id
        )
        packages = food_models.Package.objects.filter(portion__in=portions)
        data = food_models.Price.objects.filter(package__in=packages)
        sum_value = 0
        count = 0.000000000001
        for item in PriceSerializer(data, many=True).data:
            count = count + 1
            sum_value = sum_value + (item.get("price_per_kg") * (obj.weight_g / 1000))
        return round(sum_value / count, 2)


class RecipeSerializer(serializers.ModelSerializer):
    hints = food_serializers.HintSerializer(many=True, required=False)
    tags = food_serializers.TagSerializer(many=True, required=False)
    recipe_items = RecipeItemReadSerializer(many=True, read_only=True)
    allow_edit = serializers.SerializerMethodField()

    class Meta:
        model = food_models.Recipe
        fields = (
            "id",
            "name",
            "description",
            "tags",
            "get_meal_type_display",
            "meal_type",
            "nutri_class",
            "nutri_points",
            "weight_g",
            "hints",
            "recipe_items",
            "tags",
            "hints",
            "energy_kj",
            "protein_g",
            "fat_g",
            "fat_sat_g",
            "sugar_g",
            "sodium_mg",
            "salt_g",
            "fruit_factor",
            "carbohydrate_g",
            "fibre_g",
            "fructose_g",
            "lactose_g",
            "status",
            "created_at",
            "created_by",
            "updated_at",
            "allow_edit",
        )

    def get_allow_edit(self, obj):
        try:
            request = self.context.get("request")
            token = request.META.get("HTTP_AUTHORIZATION")
            child_ids = get_groups_of_user(token, request.user.keycloak_id)
            status_group = (
                KeycloakGroup.objects.filter(keycloak_id__in=child_ids)
                .filter(name__in=["DPV AK Digitales", "FoodInspi"])
                .exists()
            )
            status_user = (
                food_models.Recipe.objects.filter(id=obj.id)
                .filter(created_by__id=request.user.id)
                .exists()
            )
            return status_user or status_group
        except:
            return False

    def to_representation(self, instance):
        data = super(RecipeSerializer, self).to_representation(instance)

        data["price_eur"] = AggLib.agg_recipe_sum(self, data, "price")
        return data


class RecipeDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = food_models.Recipe
        fields = (
            "id",
            "name",
            "nutri_class",
            "nutri_points",
            "weight_g",
            "energy_kj",
            "protein_g",
            "fat_g",
            "fat_sat_g",
            "sugar_g",
            "sodium_mg",
            "salt_g",
            "meal_type",
        )

    def to_representation(self, instance):
        data = super(RecipeDataSerializer, self).to_representation(instance)
        return data


class RetailerSerializer(serializers.ModelSerializer):
    class Meta:
        model = food_models.Retailer
        fields = "__all__"


class PhysicalActivityLevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = food_models.PhysicalActivityLevel
        fields = "__all__"


class PackageSerializer(serializers.ModelSerializer):
    price_per_kg = serializers.SerializerMethodField()

    class Meta:
        model = food_models.Package
        fields = (
            "id",
            "name",
            "quality",
            "quantity",
            "weight_package_g",
            "price_per_kg",
        )

    def get_price_per_kg(self, obj):
        data = food_models.Price.objects.filter(package=obj)
        sum_value = 0
        count = 0.000000000001
        for item in PriceSerializer(data, many=True).data:
            count = count + 1
            sum_value = sum_value + item.get("price_per_kg")
        return round(sum_value / count, 2)


class PackageReadSerializer(serializers.ModelSerializer):
    price_per_kg = serializers.SerializerMethodField()
    portion = PortionSerializer(many=False, read_only=True)

    class Meta:
        model = food_models.Package
        fields = (
            "id",
            "name",
            "portion",
            "quality",
            "quantity",
            "weight_package_g",
            "price_per_kg",
        )

    def get_price_per_kg(self, obj):
        data = food_models.Price.objects.filter(package=obj)
        sum_value = 0
        count = 0.000000000001
        for item in PriceSerializer(data, many=True).data:
            count = count + 1
            sum_value = sum_value + item.get("price_per_kg")
        return round(sum_value / count, 2)


class PackageReadPollSerializer(serializers.ModelSerializer):
    class Meta:
        model = food_models.Package
        fields = (
            "id",
            "name",
        )


class PollItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = food_models.PollItem
        fields = "__all__"


class PackageReadPollSerializer(serializers.ModelSerializer):
    class Meta:
        model = food_models.Package
        fields = (
            "id",
            "name",
        )


class PriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = food_models.Price
        fields = ("id", "price_eur", "retailer", "package", "price_per_kg")


class PriceReadSerializer(serializers.ModelSerializer):
    package = PackageSerializer(many=False, read_only=True)
    retailer = RetailerSerializer(many=False, read_only=True)

    class Meta:
        model = food_models.Price
        fields = (
            "id",
            "price_eur",
            "retailer",
            "package",
            "price_per_kg",
            "created_at",
        )


class MealItemReadSerializer(serializers.ModelSerializer):
    recipe = RecipeSerializer(many=False, read_only=True)
    energy_kj = serializers.SerializerMethodField()
    nutri_points = serializers.SerializerMethodField()
    weight_g = serializers.SerializerMethodField()

    class Meta:
        model = food_models.MealItem
        fields = (
            "id",
            "recipe",
            "meal",
            "factor",
            "energy_kj",
            "nutri_points",
            "weight_g",
        )

    def get_energy_kj(self, obj):
        return round(obj.recipe.energy_kj * obj.factor, 0)

    def get_nutri_points(self, obj):
        return round(obj.recipe.nutri_points * obj.factor, 1)

    def get_weight_g(self, obj):
        return round(obj.recipe.weight_g * obj.factor, 0)

    def to_representation(self, instance):
        data = super(MealItemReadSerializer, self).to_representation(instance)
        data["price_eur"] = AggLib.agg_meal_items_sum(self, data, "price")
        return data


class MealItemReadExtendedSerializer(serializers.ModelSerializer):
    recipe = RecipeSerializer(many=False, read_only=True)

    class Meta:
        model = food_models.MealItem
        fields = "__all__"


class MealItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = food_models.MealItem
        fields = "__all__"


class MealDaySerializer(serializers.ModelSerializer):
    class Meta:
        model = food_models.MealDay
        fields = "__all__"


class MealEventSmallSerializer(serializers.ModelSerializer):
    event = event_serializers.EventFoodSerializer(many=False, read_only=True)
    created_by = registration_serializers.CurrentUserSerializer(
        many=True, read_only=True
    )

    class Meta:
        model = food_models.MealEvent
        fields = "__all__"


class MealDayShortSerializer(serializers.ModelSerializer):
    activity_factor = food_serializers.PhysicalActivityLevelSerializer(
        many=False, read_only=True
    )
    meal_event = MealEventSmallSerializer(many=False, read_only=True)

    class Meta:
        model = food_models.MealDay
        fields = "__all__"


class MealReadSerializer(serializers.ModelSerializer):
    meal_items = serializers.SerializerMethodField()
    meal_day = MealDayShortSerializer(many=False, read_only=True)

    class Meta:
        model = food_models.Meal
        fields = (
            "id",
            "name",
            "meal_day",
            "day_part_factor",
            "meal_type",
            "get_meal_type_display",
            "meal_items",
            "time_start",
            "time_end",
        )

    def get_meal_items(self, obj):
        data = food_models.MealItem.objects.filter(meal=obj)
        return MealItemReadSerializer(data, many=True).data

    def to_representation(self, instance):
        NutriClass = Nutri()
        data = super(MealReadSerializer, self).to_representation(instance)
        data["price_eur"] = AggLib.agg_meal_sum(self, data, "price")

        data["energy_kj"] = AggLib.agg_meal_sum(self, data, "energy_kj")

        data["day_part_energy_kj"] = instance.day_part_factor and round(
            data["energy_kj"] / (11500 * instance.day_part_factor), 2
        )

        data["weight_g"] = AggLib.agg_meal_sum(self, data, "weight_g")

        if data["weight_g"] == 0:
            data["nutri_points"] = 0
        else:
            data["nutri_points"] = (
                AggLib.agg_meal_sum(self, data, ["weight_g", "nutri_points"])
                / data["weight_g"]
            )

        data["nutri_class"] = NutriClass.get_nutri_class("solid", data["nutri_points"])
        return data


class MealReadExtendedSerializer(serializers.ModelSerializer):
    meal_items = serializers.SerializerMethodField()

    class Meta:
        model = food_models.Meal
        fields = "__all__"

    def get_meal_items(self, obj):
        jjj = food_models.MealItem.objects.filter(meal=obj)
        return MealItemReadExtendedSerializer(jjj, many=True).data


class MealSerializer(serializers.ModelSerializer):
    class Meta:
        model = food_models.Meal
        fields = "__all__"


class MealDayReadSerializer(serializers.ModelSerializer):
    meals = serializers.SerializerMethodField()
    allow_edit = serializers.SerializerMethodField()

    class Meta:
        model = food_models.MealDay
        fields = "__all__"

    def get_allow_edit(self, obj):
        try:
            request = self.context.get("request")
            token = request.META.get("HTTP_AUTHORIZATION")
            child_ids = get_groups_of_user(token, request.user.keycloak_id)
            status_group = (
                KeycloakGroup.objects.filter(keycloak_id__in=child_ids)
                .filter(name__in=["DPV AK Digitales", "FoodInspi"])
                .exists()
            )
            status_user = (
                food_models.Recipe.objects.filter(id=obj.id)
                .filter(created_by__id=request.user.id)
                .exists()
            )
            return status_user or status_group
        except:
            return False

    def get_meals(self, obj):
        data = food_models.Meal.objects.filter(meal_day=obj).order_by("time_start")
        return MealReadSerializer(data, many=True).data

    def to_representation(self, instance):
        NutriClass = Nutri()
        data = super(MealDayReadSerializer, self).to_representation(instance)
        data["price_eur"] = AggLib.agg_meal_day_sum(self, data, "price")

        data["energy_kj"] = AggLib.agg_meal_day_sum(self, data, "energy_kj")

        data["day_factors"] = AggLib.agg_day_factors(self, data)

        data["energy_kj_sum"] = round(float(data["max_day_part_factor"]) * 11595.15, 0)

        data["weight_g"] = AggLib.agg_meal_day_sum(self, data, "weight_g")

        if data["weight_g"] == 0:
            data["nutri_points"] = 0
        else:
            data["nutri_points"] = (
                AggLib.agg_meal_day_sum(self, data, ["weight_g", "nutri_points"])
                / data["weight_g"]
            )

        data["nutri_class"] = NutriClass.get_nutri_class("solid", data["nutri_points"])
        return data


class MealDayReadExtendedSerializer(serializers.ModelSerializer):
    meals = serializers.SerializerMethodField()

    class Meta:
        model = food_models.MealDay
        fields = "__all__"

    def get_meals(self, obj):
        data = food_models.Meal.objects.filter(meal_day=obj)
        return MealReadExtendedSerializer(data, many=True).data

    def to_representation(self, instance):
        NutriClass = Nutri()
        data = super(MealDayReadExtendedSerializer, self).to_representation(instance)
        data["price_eur"] = AggLib.agg_meal_day_sum(self, data, "price")

        data["energy_kj"] = AggLib.agg_meal_day_sum(self, data, "energy_kj")

        data["weight_g"] = AggLib.agg_meal_day_sum(self, data, "weight_g")

        if data["weight_g"] == 0:
            data["nutri_points"] = 0
        else:
            data["nutri_points"] = (
                AggLib.agg_meal_day_sum(self, data, ["weight_g", "nutri_points"])
                / data["weight_g"]
            )

        data["nutri_class"] = NutriClass.get_nutri_class("solid", data["nutri_points"])
        return data


class MealEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = food_models.MealEvent
        fields = "__all__"


class MealEventReadSerializer(serializers.ModelSerializer):
    event = event_serializers.EventFoodSerializer(many=False, read_only=True)
    activity_factor = food_serializers.PhysicalActivityLevelSerializer(
        many=False, read_only=True
    )
    meal_days = serializers.SerializerMethodField()
    allow_edit = serializers.SerializerMethodField()

    class Meta:
        model = food_models.MealEvent
        fields = (
            "id",
            "event",
            "description",
            "norm_portions",
            "activity_factor",
            "reserve_factor",
            "is_public",
            "is_approved",
            "created_by",
            "allow_edit",
            "meal_days",
            "event",
        )

    def get_meal_days(self, obj):
        jjj = food_models.MealDay.objects.filter(meal_event=obj).order_by("date")
        return MealDayReadSerializer(jjj, many=True).data

    def get_allow_edit(self, obj):
        try:
            request = self.context.get("request")
            token = request.META.get("HTTP_AUTHORIZATION")
            child_ids = get_groups_of_user(token, request.user.keycloak_id)
            status_group = (
                KeycloakGroup.objects.filter(keycloak_id__in=child_ids)
                .filter(name__in=["DPV AK Digitales", "FoodInspi"])
                .exists()
            )
            status_user = (
                food_models.MealEvent.objects.filter(id=obj.id)
                .filter(created_by__id=request.user.id)
                .exists()
            )
            return status_user or status_group
        except:
            return False

    def to_representation(self, instance):
        NutriClass = Nutri()
        data = super(MealEventReadSerializer, self).to_representation(instance)
        data["price_eur"] = AggLib.agg_meal_event_sum(self, data, "price")

        data["energy_kj"] = AggLib.agg_meal_event_sum(self, data, "energy_kj")
        data["energy_kj_sum"] = AggLib.agg_meal_event_energy_kj(self, data)

        data["weight_g"] = AggLib.agg_meal_event_sum(self, data, "weight_g")

        if data["weight_g"] == 0:
            data["nutri_points"] = 0
        else:
            data["nutri_points"] = (
                AggLib.agg_meal_event_sum(self, data, ["weight_g", "nutri_points"])
                / data["weight_g"]
            )

        data["nutri_class"] = NutriClass.get_nutri_class("solid", data["nutri_points"])
        return data


class EventReadExtendedSerializer(serializers.ModelSerializer):
    event = event_serializers.EventFoodSerializer(many=False, read_only=True)
    meal_days = serializers.SerializerMethodField()

    class Meta:
        model = food_models.MealEvent
        fields = "__all__"

    def get_meal_days(self, obj):
        data = food_models.MealDay.objects.filter(meal_event=obj)
        return MealDayReadExtendedSerializer(data, many=True).data

    def to_representation(self, instance):
        data = super(EventReadExtendedSerializer, self).to_representation(instance)
        return data
