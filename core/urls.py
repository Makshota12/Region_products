from rest_framework.routers import DefaultRouter
from .views import ProductViewSet, DomainViewSet, CriterionViewSet, RatingScaleViewSet

router = DefaultRouter()
router.register(r'products', ProductViewSet)
router.register(r'domains', DomainViewSet)
router.register(r'criteria', CriterionViewSet)
router.register(r'rating-scales', RatingScaleViewSet)

urlpatterns = router.urls

