from django.urls import include, path
from rest_framework_nested import routers

from . import views

router = routers.SimpleRouter()
router.register(r"measuring-unit", views.MeasuringUnitViewSet)

router.register(r"price", views.PriceViewSet)
router.register(r"price-read", views.PriceReadViewSet)

router.register(r"tag-category", views.TagCategoryViewSet)
router.register(r"tag", views.TagViewSet)

router.register(r"ingredient", views.IngredientViewSet)

router.register(r"recipe", views.RecipeViewSet)
router.register(r"recipe-read", views.RecipeReadViewSet)
router.register(
    r"recipe-read-verified",
    views.RecipeReadVerifiedViewSet,
    basename="recipe-read-verified",
)
router.register(
    r"recipe-read-user", views.RecipeReadUserViewSet, basename="recipe-read-user"
)
router.register(r"my-recipe-read", views.MyRecipeReadViewSet, basename="my-recipe-read")
router.register(r"recipe-item", views.RecipeItemViewSet, basename="recipe-item")
router.register(r"recipe-clone", views.RecipeCloneViewSet, basename="recipe-clone")
router.register(r"multiply-recipe-items", views.MultiplyRecipeItemsViewSet, basename="multiply-recipe-items")

router.register(r"package", views.PackageViewSet)
router.register(r"package-read", views.PackageReadViewSet)
router.register(r"package-random-poll", views.PackageRandomPollViewSet)
router.register(r"poll-item", views.PollItemLevelViewSet)

router.register(r"retailer", views.RetailerViewSet)

router.register(r"physical-activity", views.PhysicalActivityLevelViewSet)

router.register(r"portion", views.PortionViewSet)
router.register(r"portion-read", views.PortionReadViewSet)

router.register(r"hint", views.HintViewSet)

router.register(r"meal-event", views.MealEventViewSet)
router.register(r"meal-event-read", views.MealEventReadViewSet)
router.register(r"meal-event-read-small", views.MealEventSmallReadViewSet)
router.register(
    r"my-event-read", views.MyMealEventReadViewSet, basename="my-event-read"
)
router.register(
    r"public-event-read", views.PublicMealEventReadViewSet, basename="public-event-read"
)
router.register(
    r"approved-event-read",
    views.ApprovedMealEventReadViewSet,
    basename="approved-event-read",
)

router.register(r"meal-day", views.MealDayViewSet)
router.register(r"meal-day-read", views.MealDayReadViewSet)
router.register(r"meal", views.MealViewSet)
router.register(r"meal-clone", views.MealCloneViewSet, basename="meal-clone")
router.register(r"meal-item", views.MealItemViewSet)

# Choices
router.register(r"gender", views.GenderViewSet, basename="gender")
router.register(r"meal-types", views.MealTypeViewSet, basename="meal-types")
router.register(r"major-class", views.MajorClassViewSet, basename="major-class")
router.register(r"recipe-statuses", views.RecipeStatusViewSet, basename="major-class")

# Shopping-List
router.register(r"shopping-list", views.ShoppingListViewSet, basename="shopping-list")

urlpatterns = [
    path("", include(router.urls)),
]
