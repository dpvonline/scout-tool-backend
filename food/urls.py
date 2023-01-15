from django.urls import include, path
from rest_framework_nested import routers

from . import views

router = routers.SimpleRouter()
router.register(r'measuring-unit', views.MeasuringUnitViewSet)

router.register(r'price', views.PriceViewSet)
router.register(r'price-read', views.PriceReadViewSet)

router.register(r'tag-category', views.TagCategoryViewSet)
router.register(r'tag', views.TagViewSet)

router.register(r'ingredient', views.IngredientViewSet)

router.register(r'recipe', views.RecipeViewSet)
router.register(r'recipe-read', views.RecipeReadViewSet)
router.register(r'recipe-read-verified', views.RecipeReadVerifiedViewSet)
router.register(r'recipe-item', views.RecipeItemViewSet)
router.register(r'recipe-clone', views.RecipeCloneViewSet, basename='recipe-clone')

router.register(r'package', views.PackageViewSet)
router.register(r'package-read', views.PackageReadViewSet)

router.register(r'retailer', views.RetailerViewSet)

router.register(r'physical-activity', views.PhysicalActivityLevelViewSet)

router.register(r'portion', views.PortionViewSet)
router.register(r'portion-read', views.PortionReadViewSet)

router.register(r'hint', views.HintViewSet)

router.register(r'event', views.EventViewSet)
router.register(r'event-read', views.EventReadViewSet)
router.register(r'event-read-small', views.EventSmallReadViewSet)

router.register(r'meal-day', views.MealDayViewSet)
router.register(r'meal-day-read', views.MealDayReadViewSet)
router.register(r'meal', views.MealViewSet)
router.register(r'meal-item', views.MealItemViewSet)

# Choices
router.register(r'gender', views.GenderViewSet, basename='gender')
router.register(r'meal-types', views.MealTypeViewSet, basename='meal-types')
router.register(r'major-class', views.MajorClassViewSet, basename='major-class')

# Shopping-List
router.register(r'shopping-list', views.ShoppingListViewSet, basename='shopping-list')

urlpatterns = [
    path('', include(router.urls)),
]
