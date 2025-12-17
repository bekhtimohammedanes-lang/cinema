from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.shortcuts import get_object_or_404

from .models import (
    Author,
    Spectator,
    Film,
    FilmRating,
    AuthorRating,
    Favorite,
)
from .serializers import (
    AuthorSerializer,
    FilmSerializer,
    FilmWriteSerializer,
    FilmRatingSerializer,
    AuthorRatingSerializer,
    FavoriteSerializer,
    SpectatorRegisterSerializer,
)

# =====================================================
# PERMISSIONS
# =====================================================

class IsAuthenticatedOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_authenticated


# =====================================================
# AUTHOR
# =====================================================

class AuthorViewSet(viewsets.ModelViewSet):
    queryset = Author.objects.prefetch_related("films", "user")
    serializer_class = AuthorSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


    def get_queryset(self):
        queryset = super().get_queryset()
        # Filtre par source si paramètre fourni (ADMIN ou TMDB)
        source = self.request.query_params.get("source")
        if source in ["ADMIN", "TMDB"]:
            queryset = queryset.filter(source=source)
        return queryset


    def destroy(self, request, *args, **kwargs):
        author = self.get_object()
        if author.films.exists():
            return Response(
                {"error": "Impossible de supprimer un auteur avec des films."},
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().destroy(request, *args, **kwargs)


# =====================================================
# FILM
# =====================================================

class FilmViewSet(viewsets.ModelViewSet):
    queryset = Film.objects.prefetch_related("authors")
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return FilmWriteSerializer
        return FilmSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        # Filtre par status (ex: PUBLISHED, ARCHIVED)
        status_param = self.request.query_params.get("status")
        if status_param:
            queryset = queryset.filter(status=status_param)
            
        # Filtre par source (ADMIN ou TMDB)
        source_param = self.request.query_params.get("source")
        if source_param in ["ADMIN", "TMDB"]:
            queryset = queryset.filter(source=source_param)
            
        return queryset

    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated])
    def archive(self, request, pk=None):
        film = self.get_object()
        film.status = Film.STATUS_ARCHIVED
        film.save()
        return Response({"status": "Film archivé"})


# =====================================================
# FILM RATING
# =====================================================

class FilmRatingViewSet(viewsets.ModelViewSet):
    serializer_class = FilmRatingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return FilmRating.objects.filter(spectator__user=self.request.user)

    def perform_create(self, serializer):
        spectator = get_object_or_404(Spectator, user=self.request.user)
        film_id = self.request.data.get("film")
        film = get_object_or_404(Film, id=film_id)
        serializer.save(spectator=spectator, film=film)


# =====================================================
# AUTHOR RATING
# =====================================================

class AuthorRatingViewSet(viewsets.ModelViewSet):
    serializer_class = AuthorRatingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return AuthorRating.objects.filter(spectator__user=self.request.user)

    def perform_create(self, serializer):
        spectator = get_object_or_404(Spectator, user=self.request.user)
        author_id = self.request.data.get("author")
        author = get_object_or_404(Author, id=author_id)
        serializer.save(spectator=spectator, author=author)


# =====================================================
# FAVORITES
# =====================================================

class FavoriteViewSet(viewsets.ModelViewSet):
    serializer_class = FavoriteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Favorite.objects.filter(spectator__user=self.request.user)

    def perform_create(self, serializer):
        spectator = get_object_or_404(Spectator, user=self.request.user)
        film_id = self.request.data.get("film")
        film = get_object_or_404(Film, id=film_id)
        serializer.save(spectator=spectator, film=film)


# =====================================================
# AUTH / REGISTER
# =====================================================

from rest_framework.generics import CreateAPIView

class SpectatorRegisterView(CreateAPIView):
    serializer_class = SpectatorRegisterSerializer
    permission_classes = [permissions.AllowAny]
    
    
class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()  # ajoute le token à la blacklist
            return Response({"detail": "Token révoqué"}, status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    

