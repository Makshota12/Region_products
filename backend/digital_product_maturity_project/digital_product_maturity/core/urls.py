from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import ProductViewSet, DomainViewSet, CriterionViewSet, RatingScaleViewSet, EvaluationSessionViewSet, AssignedCriterionViewSet, EvaluationAnswerViewSet, RoleViewSet, ProfileViewSet, UserViewSet, generate_portfolio_report
from .auth_views import register_user, login_user, logout_user, current_user, google_login

router = DefaultRouter()
router.register(r'products', ProductViewSet)
router.register(r'domains', DomainViewSet)
router.register(r'criteria', CriterionViewSet)
router.register(r'rating-scales', RatingScaleViewSet)
router.register(r'evaluation-sessions', EvaluationSessionViewSet)
router.register(r'assigned-criteria', AssignedCriterionViewSet)
router.register(r'evaluation-answers', EvaluationAnswerViewSet)
router.register(r'roles', RoleViewSet)
router.register(r'profiles', ProfileViewSet)
router.register(r'users', UserViewSet)

urlpatterns = router.urls
urlpatterns += [
    path('portfolio-report/', generate_portfolio_report, name='portfolio-report'),
    # Auth endpoints
    path('auth/register/', register_user, name='register'),
    path('auth/login/', login_user, name='login'),
    path('auth/google/', google_login, name='google-login'),
    path('auth/logout/', logout_user, name='logout'),
    path('auth/user/', current_user, name='current-user'),
    # Django-allauth endpoints (для Google и Telegram OAuth)
    path('auth/', include('dj_rest_auth.urls')),
    path('auth/registration/', include('dj_rest_auth.registration.urls')),
    path('auth/google-oauth/', include('allauth.socialaccount.providers.google.urls')),
    path('auth/telegram/', include('allauth.socialaccount.providers.telegram.urls')),
]
