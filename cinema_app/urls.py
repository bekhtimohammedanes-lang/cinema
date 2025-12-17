from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from .views import (
    AuthorViewSet,
    FilmViewSet,
    FilmRatingViewSet,
    AuthorRatingViewSet,
    FavoriteViewSet,
    SpectatorRegisterView,
    LogoutView,
)

router = DefaultRouter()

# Lecture publique / écriture protégée JWT
router.register(r"authors", AuthorViewSet, basename="author")
router.register(r"films", FilmViewSet, basename="film")

# Actions spectateur (JWT obligatoire)
router.register(r"ratings/films", FilmRatingViewSet, basename="film-rating")
router.register(r"ratings/authors", AuthorRatingViewSet, basename="author-rating")
router.register(r"favorites", FavoriteViewSet, basename="favorite")

urlpatterns = [
    # ==========================
    # API
    # ==========================
    path("api/", include(router.urls)),

    # ==========================
    # AUTH JWT (spectateur)
    # ==========================
    path("api/auth/register/", SpectatorRegisterView.as_view(), name="spectator-register"),
    path("api/auth/login/", TokenObtainPairView.as_view(), name="jwt-login"),
    path("api/auth/token/refresh/", TokenRefreshView.as_view(), name="jwt-refresh"),
    path("api/auth/logout/", LogoutView.as_view(), name="logout"),
]

