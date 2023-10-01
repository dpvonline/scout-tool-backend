from food import models as food_models
from django.db.models import Sum
from food.service.nutri_lib import Nutri


def agg_func(obj, agg_field):
    if isinstance(agg_field, str):
        return obj.get(agg_field)
    if isinstance(agg_field, list):
        return obj.get(agg_field[0]) * obj.get(agg_field[1])


def get_agg_recipe(recipes, agg_field):
    total = 0
    for recipe_keys, recipe_values in recipes.items():
        if recipe_keys == "recipe_items":
            for recipe_item in recipe_values:
                total += agg_func(recipe_item, agg_field)
    return total


def get_agg_meal_items(meal_items, agg_field):
    total = 0
    for meal_item_keys, meal_item_values in meal_items.items():
        if meal_item_keys == "recipe":
            total += get_agg_recipe(meal_item_values, agg_field)
    return total


def get_agg_meal(meals, agg_field):
    total = 0
    for meal_keys, meal_values in meals.items():
        if meal_keys == "meal_items":
            for meal_item in meal_values:
                total += get_agg_meal_items(meal_item, agg_field)
    return total

def get_agg_day(meal_days, agg_field):
    total = 0
    for meal_days_keys, meal_days_values in meal_days.items():
        if meal_days_keys == "meals" and meal_days_values and meal_days_values[0]:
            for meal_days_value in meal_days_values:
                total += get_agg_meal(meal_days_value, agg_field)
    return total


def get_agg_meal_event(events, agg_field):
    total = 0
    for event_keys, event_values in events.items():
        if event_keys == "meal_days":
            for meal_day in event_values:
                total += get_agg_day(meal_day, agg_field)
    return total


class Price:
    def agg_meal_items_sum(self, meal_items, agg_field):
        return get_agg_meal_items(meal_items, agg_field)

    def agg_meal_day_sum(self, meal_days, agg_field):
        return get_agg_day(meal_days, agg_field)

    def agg_recipe_sum(self, meal_days, agg_field):
        return get_agg_recipe(meal_days, agg_field)

    def agg_meal_event_sum(self, meal_days, agg_field):
        return get_agg_meal_event(meal_days, agg_field)

    def agg_meal_sum(self, meals, agg_field):
        return get_agg_meal(meals, agg_field)
