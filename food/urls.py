from django.urls import include, path
from rest_framework_nested import routers

from . import views

router = routers.SimpleRouter()
router.register(r'measuring-unit', views.MeasuringUnitViewSet)
router.register(r'price', views.PriceViewSet)
router.register(r'tag-category', views.TagCategoryViewSet)
router.register(r'tag', views.TagViewSet)
router.register(r'ingredient', views.IngredientViewSet)
router.register(r'recipe', views.RecipeViewSet)
router.register(r'recipe-read', views.RecipeReadViewSet)
router.register(r'recipe-item', views.RecipeItemViewSet)
router.register(r'package', views.PackageViewSet)
router.register(r'retailer', views.RetailerViewSet)
router.register(r'portion', views.PortionViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
