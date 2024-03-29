from django.db.models import Q, QuerySet
from django_filters import CharFilter, NumberFilter
from django_filters.rest_framework import DjangoFilterBackend, FilterSet
from rest_framework import viewsets, status
from rest_framework.exceptions import PermissionDenied, NotFound
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from food.choices import Gender
from basic.helper.choice_to_json import choice_to_json
from rest_framework.views import APIView
from rest_framework.mixins import RetrieveModelMixin

from copy import deepcopy
from itertools import groupby
from datetime import date, timedelta
import datetime

from food import models as food_models
from food import serializers as food_serializers
from anmelde_tool.event import models as event_models


def get_formatted_date(date: str) -> datetime.datetime:
    return datetime.strptime(date, "%Y-%m-%dT%H:%M")


class MeasuringUnitViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = food_models.MeasuringUnit.objects.all()
    serializer_class = food_serializers.MeasuringUnitSerializer


class HintViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = food_models.Hint.objects.all()
    serializer_class = food_serializers.HintSerializer


class PriceReadViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = food_models.Price.objects.all().order_by("-created_at")
    serializer_class = food_serializers.PriceReadSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ["id", "package__portion__ingredient__id"]


class PriceViewSet(viewsets.ModelViewSet):
    queryset = food_models.Price.objects.all()
    serializer_class = food_serializers.PriceSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ["id", "package__portion__ingredient__id"]

    def create(self, request, *args, **kwargs) -> Response:
        request.data["retailer"] = request.data["retailer"]["id"]
        if isinstance(request.data["package"], object) and request.data["package"]:
            request.data["package"] = request.data["package"]["id"]
        else:
            new_package = food_models.Package.objects.create(
                name=request.data["name"],
                portion=get_object_or_404(
                    food_models.Portion, id=request.data["portion"]["id"]
                ),
                quantity=request.data["quantity"],
                quality=request.data["quality"],
            )
            request.data["package"] = new_package.id

        return super().create(request, *args, **kwargs)


class TagCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = food_models.TagCategory.objects.all()
    serializer_class = food_serializers.TagCategorySerializer


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = food_models.Tag.objects.all()
    serializer_class = food_serializers.TagSerializer


class IngredientFilter(FilterSet):
    nutri_class = NumberFilter(field_name="nutri_class")
    physical_viscosity = CharFilter(field_name="physical_viscosity")


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = food_models.Ingredient.objects.all()
    serializer_class = food_serializers.IngredientSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = IngredientFilter
    ordering = ["name"]
    ordering_fields = ["name", "created_at", "nutri_points"]
    filterset_fields = ["name"]
    search_fields = ["name"]


class RecipeItemViewSet(viewsets.ModelViewSet):
    queryset = food_models.RecipeItem.objects.all()
    serializer_class = food_serializers.RecipeItemSerializer


class RecipeCloneViewSet(viewsets.ViewSet):
    def create(self, request, *args, **kwargs) -> Response:
        if request.data.get("id", None) is not None:
            recipe_id = request.data.get("id")
            old_recipe_obj = food_models.Recipe.objects.filter(id=recipe_id).first()
            new_old_obj = deepcopy(old_recipe_obj)
            new_old_obj.id = None
            new_old_obj.status = "simulator"
            new_old_obj.save()

            new_old_obj.created_by.add(request.user.id)

            all_items = food_models.RecipeItem.objects.filter(recipe_id=recipe_id)

            for item in all_items:
                new = deepcopy(item)
                new.id = None
                new.recipe = new_old_obj
                new.save()
            return Response(
                food_serializers.RecipeSerializer(new_old_obj).data,
                status=status.HTTP_201_CREATED,
            )

        return Response({"Bitte ID mitgeben"}, status=status.HTTP_400_BAD_REQUEST)


class MealCloneViewSet(viewsets.ViewSet):
    def create(self, request, *args, **kwargs) -> Response:
        if (
            request.data.get("clone_meal_id", None) is not None
            and request.data.get("meal_id", None) is not None
        ):
            clone_meal_id = request.data.get("clone_meal_id")
            meal_id = request.data.get("meal_id")
            current_meal_obj = food_models.Meal.objects.filter(id=meal_id).first()

            all_meal_items = food_models.MealItem.objects.filter(meal_id=clone_meal_id)

            for meal_item in all_meal_items:
                new_meal_item = deepcopy(meal_item)
                new_meal_item.id = None
                new_meal_item.meal = current_meal_obj
                new_meal_item.save()

            return Response(
                food_serializers.MealReadSerializer(current_meal_obj).data,
                status=status.HTTP_201_CREATED,
            )

        return Response({"Bitte ID mitgeben"}, status=status.HTTP_400_BAD_REQUEST)


class MultiplyRecipeItemsViewSet(viewsets.ViewSet):
    def create(self, request, *args, **kwargs) -> Response:
        if request.data.get("id", None) is not None:
            recipe_id = request.data.get("id")
            recipe_obj = food_models.Recipe.objects.filter(id=recipe_id).first()

            all_items = food_models.RecipeItem.objects.filter(recipe_id=recipe_id)

            for item in all_items:
                factor = float(str(request.data.get("factor")).replace(",", "."))
                item.quantity = item.quantity * factor
                item.save()

            return Response(
                food_serializers.RecipeSerializer(recipe_obj).data,
                status=status.HTTP_201_CREATED,
            )

        return Response({"Bitte ID mitgeben"}, status=status.HTTP_400_BAD_REQUEST)


class MealScaleViewSet(viewsets.ViewSet):
    def create(self, request, *args, **kwargs) -> Response:
        if request.data.get("id", None) is not None:
            meal_id = request.data.get("id")

            meal_data = food_models.Meal.objects.filter(id=meal_id).first()

            meal = food_serializers.MealReadSerializer(meal_data).data
            day_part_energy_kj = meal.get("day_part_energy_kj")

            all_items = food_models.MealItem.objects.filter(meal=meal_id)

            for item in all_items:
                item.factor = round(item.factor / day_part_energy_kj, 2)
                item.save()

            return Response(
                {"message": "Meal scaled"},
                status=status.HTTP_201_CREATED,
            )

        return Response({"Bitte ID mitgeben"}, status=status.HTTP_400_BAD_REQUEST)


class RecipeFilter(FilterSet):
    nutri_class = NumberFilter(field_name="nutri_class")
    status = CharFilter(field_name="status")
    meal_type = CharFilter(field_name="meal_type")


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = food_models.Recipe.objects.all()
    serializer_class = food_serializers.RecipeSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = RecipeFilter
    ordering = ["name"]
    ordering_fields = ["name", "created_at", "nutri_points"]
    filterset_fields = ["name", "meal_type"]
    search_fields = ["name"]


class RecipeReadViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = food_models.Recipe.objects.all()
    serializer_class = food_serializers.RecipeSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = RecipeFilter
    ordering = ["name"]
    ordering_fields = ["name", "created_at", "nutri_points"]
    filterset_fields = ["name", "status"]
    search_fields = ["name"]

    def get_queryset(self) -> QuerySet:
        return food_models.Recipe.objects.filter(
            Q(status="verified") | Q(status="user_public")
        )


class RecipeReadVerifiedViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = food_serializers.RecipeSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = RecipeFilter
    ordering = ["name"]
    ordering_fields = ["name", "created_at", "nutri_points"]
    filterset_fields = ["name", "meal_type"]
    search_fields = ["name"]

    def get_queryset(self) -> QuerySet:
        return food_models.Recipe.objects.filter(status="verified")


class RecipeReadUserViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = food_serializers.RecipeSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = RecipeFilter
    ordering = ["name"]
    ordering_fields = ["name", "created_at", "nutri_points"]
    filterset_fields = ["name", "meal_type"]
    search_fields = ["name"]

    def get_queryset(self) -> QuerySet:
        return food_models.Recipe.objects.filter(status="user_public")


class MyRecipeReadViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = food_serializers.RecipeSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = RecipeFilter
    ordering = ["name"]
    ordering_fields = ["name", "created_at", "nutri_points"]
    filterset_fields = ["name", "meal_type"]
    search_fields = ["name"]

    def get_queryset(self) -> QuerySet:
        return food_models.Recipe.objects.filter(
            created_by__id=self.request.user.id
        ).exclude(created_by=None)


class RetailerViewSet(viewsets.ModelViewSet):
    queryset = food_models.Retailer.objects.all()
    serializer_class = food_serializers.RetailerSerializer


class PhysicalActivityLevelViewSet(viewsets.ModelViewSet):
    queryset = food_models.PhysicalActivityLevel.objects.all()
    serializer_class = food_serializers.PhysicalActivityLevelSerializer


class PollItemLevelViewSet(viewsets.ModelViewSet):
    queryset = food_models.PollItem.objects.all()
    serializer_class = food_serializers.PollItemSerializer


class PackageViewSet(viewsets.ModelViewSet):
    queryset = food_models.Package.objects.all()
    serializer_class = food_serializers.PackageSerializer


class PackageReadViewSet(viewsets.ModelViewSet):
    queryset = food_models.Package.objects.all()
    serializer_class = food_serializers.PackageReadSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ["portion__ingredient__id"]


class PackageRandomPollViewSet(viewsets.ModelViewSet):
    queryset = food_models.Package.objects.order_by("?")[:2]
    serializer_class = food_serializers.PackageReadPollSerializer


class PortionViewSet(viewsets.ModelViewSet):
    queryset = food_models.Portion.objects.all().order_by("rank").order_by("name")
    serializer_class = food_serializers.PortionSerializer

    def create(self, request, *args, **kwargs) -> Response:
        if request.data.get("name", None) is None:
            ingredient = food_models.Ingredient.objects.filter(
                id=request.data.get("ingredient")
            ).first()
            measuring_unit_name = request.data["measuring_unit"]["name"]
            request.data["name"] = f"{ingredient.name} in {measuring_unit_name} "

        request.data["measuring_unit"] = request.data["measuring_unit"]["id"]
        return super().create(request, *args, **kwargs)


class PortionReadViewSet(viewsets.ModelViewSet):
    queryset = food_models.Portion.objects.all().order_by("name").order_by("rank")
    serializer_class = food_serializers.PortionReadSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ["id", "name", "ingredient__id"]
    search_fields = ["name", "ingredient__name"]


class MealEventViewSet(viewsets.ModelViewSet):
    queryset = food_models.MealEvent.objects.all()
    serializer_class = food_serializers.MealEventSerializer

    def create(self, request, *args, **kwargs) -> Response:
        selected_event = event_models.Event.objects.filter(
            id=request.data.get("event")
        ).first()

        activity_factor_id = request.data.get("activity_factor")

        activity_factor = food_models.PhysicalActivityLevel.objects.filter(
            id=activity_factor_id
        ).first()

        new_meal_event = food_models.MealEvent.objects.create(
            event=selected_event,
            norm_portions=request.data.get("norm_portions"),
            description=request.data.get("description"),
            activity_factor=activity_factor,
            reserve_factor=request.data.get("reserve_factor"),
            is_public=request.data.get("is_public"),
            is_approved=request.data.get("is_approved"),
        )

        new_meal_event.created_by.add(request.user.id)

        start_date = selected_event.start_date
        end_date = selected_event.end_date

        day_count = (end_date.date() - start_date.date()).days + 1

        for single_date in (start_date + timedelta(n) for n in range(day_count)):
            tomorrow = single_date + timedelta(days=1)

            tomorrow_with_time = datetime.datetime(
                year=tomorrow.year,
                month=tomorrow.month,
                day=tomorrow.day,
            )

            today_with_time = datetime.datetime(
                year=single_date.year,
                month=single_date.month,
                day=single_date.day,
            )

            hours_left = (
                tomorrow_with_time.timestamp() - start_date.timestamp()
            ) / 3600
            hours_until = (end_date.timestamp() - today_with_time.timestamp()) / 3600

            print(hours_until)

            if hours_left < 24:
                max_day_part_factor = hours_left / 24
            elif hours_until < 24:
                max_day_part_factor = hours_until / 24
            else:
                max_day_part_factor = 1

            current_meal_day = food_models.MealDay.objects.create(
                date=single_date,
                meal_event=new_meal_event,
                max_day_part_factor=max_day_part_factor,
            )
            current_date = single_date.date()

            start_date_ts = selected_event.start_date.timestamp()
            end_date_ts = selected_event.end_date.timestamp()

            food_models.Meal.objects.create(
                name="Snacks",
                meal_day=current_meal_day,
                day_part_factor=0.10,
                meal_type="snack",
                time_start=datetime.time(7, 00),
                time_end=datetime.time(22, 00),
            )

            food_models.Meal.objects.create(
                name="Getränke",
                meal_day=current_meal_day,
                day_part_factor=0.00,
                meal_type="snack",
                time_start=datetime.time(7, 00),
                time_end=datetime.time(22, 00),
            )

            dt_breakfast = datetime.datetime.combine(
                current_date, datetime.time(8, 00)
            ).timestamp()

            if start_date_ts < dt_breakfast < end_date_ts:
                food_models.Meal.objects.create(
                    name="Frühstück",
                    meal_day=current_meal_day,
                    day_part_factor=0.30,
                    meal_type="breakfast",
                    time_start=datetime.time(8, 00),
                    time_end=datetime.time(9, 00),
                )

            dt_lunch = datetime.datetime.combine(
                current_date, datetime.time(13, 00)
            ).timestamp()
            if start_date_ts < dt_lunch < end_date_ts:
                food_models.Meal.objects.create(
                    name="Mittagessen",
                    meal_day=current_meal_day,
                    day_part_factor=0.30,
                    meal_type="lunch_cold",
                    time_start=datetime.time(13, 00),
                    time_end=datetime.time(14, 00),
                )

            dt_dinner = datetime.datetime.combine(
                current_date, datetime.time(19, 00)
            ).timestamp()
            if start_date_ts < dt_dinner < end_date_ts:
                food_models.Meal.objects.create(
                    name="Abendessen",
                    meal_day=current_meal_day,
                    day_part_factor=0.30,
                    meal_type="lunch_warm",
                    time_start=datetime.time(19, 00),
                    time_end=datetime.time(20, 00),
                )

                food_models.Meal.objects.create(
                    name="Abendsnack",
                    meal_day=current_meal_day,
                    day_part_factor=0.10,
                    meal_type="snack",
                    time_start=datetime.time(21, 00),
                    time_end=datetime.time(22, 00),
                )

        return Response(
            food_serializers.MealEventReadSerializer(new_meal_event).data,
            status=status.HTTP_201_CREATED,
        )

    def update(self, request, *args, **kwargs) -> Response:
        current_meal_event = food_models.MealEvent.objects.filter(
            id=request.data.get("id")
        ).first()
        return super().update(request, *args, **kwargs)


class MealEventReadViewSet(viewsets.ModelViewSet):
    queryset = food_models.MealEvent.objects.all()
    serializer_class = food_serializers.MealEventReadSerializer


class MealEventSmallReadViewSet(viewsets.ModelViewSet):
    queryset = food_models.MealEvent.objects.all()
    serializer_class = food_serializers.MealEventSmallSerializer


class MyMealEventReadViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = food_serializers.MealEventReadSerializer

    def get_queryset(self) -> QuerySet:
        return food_models.MealEvent.objects.filter(
            created_by__id=self.request.user.id
        ).exclude(created_by=None)


class MyMealEventSmallReadViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = food_serializers.MealEventSmallSerializer

    def get_queryset(self) -> QuerySet:
        return food_models.MealEvent.objects.filter(
            created_by__id=self.request.user.id
        ).exclude(created_by=None)


class PublicMealEventReadViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = food_serializers.MealEventReadSerializer

    def get_queryset(self) -> QuerySet:
        return food_models.MealEvent.objects.filter(
            Q(is_public=True) | Q(created_by__id=self.request.user.id)
        )


class PublicMealEventSmallReadViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = food_serializers.MealEventSmallSerializer

    def get_queryset(self) -> QuerySet:
        return food_models.MealEvent.objects.filter(
            Q(is_public=True) | Q(created_by__id=self.request.user.id)
        ).distinct()


class ApprovedMealEventReadViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = food_serializers.MealEventReadSerializer

    def get_queryset(self) -> QuerySet:
        return food_models.MealEvent.objects.filter(is_approved=True, is_public=True)


class ApprovedMealEventSmallReadViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = food_serializers.MealEventSmallSerializer

    def get_queryset(self) -> QuerySet:
        return food_models.MealEvent.objects.filter(is_approved=True, is_public=True)


class MealDayViewSet(viewsets.ModelViewSet):
    queryset = food_models.MealDay.objects.all()
    serializer_class = food_serializers.MealDaySerializer


class MealDayReadViewSet(viewsets.ModelViewSet):
    queryset = food_models.MealDay.objects.all()
    serializer_class = food_serializers.MealDayReadSerializer


class MealViewSet(viewsets.ModelViewSet):
    queryset = food_models.Meal.objects.all()
    serializer_class = food_serializers.MealSerializer


class CookingPlanViewSet(viewsets.ModelViewSet):

    queryset = food_models.Meal.objects.all()
    serializer_class = food_serializers.CookingPlanSerializer

    def get_queryset(self) -> QuerySet:
        eventId: str = self.request.query_params.get("eventId", None)
        return food_models.Meal.objects.filter(
            meal_day__meal_event__id=eventId
        ).order_by("meal_day__date", "day_part_factor")


class MealItemViewSet(viewsets.ModelViewSet):
    queryset = food_models.MealItem.objects.all()
    serializer_class = food_serializers.MealItemSerializer


class GenderViewSet(viewsets.ViewSet):
    def list(self, request) -> Response:
        result = choice_to_json(Gender.choices)
        return Response(result, status=status.HTTP_200_OK)


class MealTypeViewSet(viewsets.ViewSet):
    def list(self, request) -> Response:
        result = choice_to_json(food_models.MealType.choices)
        return Response(result, status=status.HTTP_200_OK)


class RecipeStatusViewSet(viewsets.ViewSet):
    def list(self, request) -> Response:
        result = choice_to_json(food_models.RecipeStatus.choices)
        return Response(result, status=status.HTTP_200_OK)


class MajorClassViewSet(viewsets.ViewSet):
    def list(self, request) -> Response:
        result = choice_to_json(food_models.FoodMajorClasses.choices)
        return Response(result, status=status.HTTP_200_OK)


def add_agg_to_list(items):
    my_list = []
    sum_dict = {}
    weight_g = round(sum(item["weight_g"] for item in items), 0)
    weight_kg = round(sum(item["weight_kg"] for item in items), 2)
    price = round(sum(item["price"] for item in items), 2)
    sum_dict["weight_g"] = weight_g
    sum_dict["weight_kg"] = weight_kg
    sum_dict["price"] = price
    sum_dict["recipe_name"] = ", ".join(str(x["recipe_name"]) for x in items)
    sum_dict["weight_show"] = f"{weight_kg} Kg" if weight_g >= 1000 else f"{weight_g} g"

    dict_copy = sum_dict.copy()  # 👈️ create copy
    my_list.append(dict_copy)
    my_list.extend(items)

    return my_list


def stack_items(input_items):
    return_dict = {}

    for group, items in groupby(
        sorted(input_items, key=lambda x: x["ingredient_name"]),
        lambda x: x["ingredient_name"],
    ):
        return_dict[group] = add_agg_to_list(list(items))
    return return_dict


class ShoppingListViewSet(viewsets.ViewSet):
    # pylint: disable=no-self-use
    def list(self, request) -> Response:
        """
        @param request: request information
        @return: Response with serialized UserExtended instance of the user requesting the personal data
        """
        event_id = request.query_params["id"]
        queryset = food_models.MealEvent.objects.get(id=event_id)
        serializer = food_serializers.EventReadExtendedSerializer(queryset, many=False)

        return_list = []
        return_dict_class = {}

        for meal_day in serializer.data["meal_days"]:
            for meal in meal_day["meals"]:
                for meal_item in meal["meal_items"]:
                    if meal_item["recipe"] and meal_item["recipe"].get("recipe_items"):
                        for recipe_item in meal_item["recipe"].get("recipe_items"):
                            weight_g = round(
                                recipe_item.get("weight_g")
                                * meal_item.get("factor", 1.0)
                                * serializer.data.get("norm_portions"),
                                1,
                            )
                            weight_kg = round(
                                recipe_item.get("weight_g")
                                * meal_item.get("factor", 1.0)
                                * serializer.data.get("norm_portions")
                                / 1000,
                                3,
                            )
                            price = round(
                                recipe_item.get("price", 0)
                                * meal_item.get("factor", 1.0)
                                * serializer.data.get("norm_portions"),
                                2
                            )
                            return_list.append(
                                {
                                    "ingredient_name": recipe_item.get("portion")
                                    .get("ingredient")
                                    .get("name"),
                                    "ingredient_class": recipe_item.get("portion")
                                    .get("ingredient")
                                    .get("get_major_class_display"),
                                    "recipe_name": meal_item["recipe"].get("name"),
                                    "price": price,
                                    "weight_g": weight_g,
                                    "weight_kg": weight_kg,
                                    "weight_show": (
                                        f"{weight_kg} Kg"
                                        if weight_g >= 1000
                                        else f"{weight_g} g"
                                    ),
                                }
                            )

        # sort by ingredient name
        return_list = sorted(
            return_list, key=lambda x: x["ingredient_name"], reverse=False
        )

        # group by major class
        for group, items in groupby(
            sorted(return_list, key=lambda x: x["ingredient_class"]),
            lambda x: x["ingredient_class"],
        ):
            return_dict_class[group] = stack_items(list(items))

        return Response(return_dict_class)
