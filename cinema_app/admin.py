from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.db.models import Count

from .models import User, Author, Spectator, Film, FilmRating, AuthorRating, Favorite

# =========================
# INLINES
# =========================

class FilmRatingInlineForFilm(admin.TabularInline):
    model = FilmRating
    fk_name = "film"  # parent = Film
    extra = 0
    autocomplete_fields = ("spectator",)


class FilmRatingInlineForSpectator(admin.TabularInline):
    model = FilmRating
    fk_name = "spectator"  # parent = Spectator
    extra = 0
    autocomplete_fields = ("film",)


class AuthorRatingInlineForAuthor(admin.TabularInline):
    model = AuthorRating
    fk_name = "author"  # parent = Author
    extra = 0
    autocomplete_fields = ("spectator",)


class AuthorRatingInlineForSpectator(admin.TabularInline):
    model = AuthorRating
    fk_name = "spectator"  # parent = Spectator
    extra = 0
    autocomplete_fields = ("author",)


class FavoriteInline(admin.TabularInline):
    model = Favorite
    fk_name = "spectator"  # parent = Spectator
    extra = 0
    autocomplete_fields = ("film",)


# =========================
# FILM ADMIN
# =========================

@admin.register(Film)
class FilmAdmin(admin.ModelAdmin):
    list_display = ("title", "status", "evaluation", "source", "release_date", "created_at")
    list_filter = ("status", "evaluation", "source", "created_at")
    search_fields = ("title", "description")
    ordering = ("-created_at",)
    autocomplete_fields = ("authors",)
    inlines = [FilmRatingInlineForFilm]
    readonly_fields = ("created_at", "updated_at")

    fieldsets = (
        ("Informations générales", {"fields": ("title", "description", "release_date")}),
        ("Classification", {"fields": ("evaluation", "status", "source")}),
        ("Relations", {"fields": ("authors",)}),
        ("Métadonnées", {"fields": ("created_at", "updated_at")}),
    )




# Inline pour les films d’un auteur
class FilmInline(admin.TabularInline):
    model = Film.authors.through  
    extra = 0
    verbose_name = "Film"
    verbose_name_plural = "Films"
    autocomplete_fields = ("film",) 


# =========================
# FILTRE AUTEURS AVEC FILMS
# =========================
class HasFilmsFilter(admin.SimpleListFilter):
    title = "Auteurs avec films"
    parameter_name = "has_films"

    def lookups(self, request, model_admin):
        return (
            ("yes", "Avec au moins un film"),
            ("no", "Sans film"),
        )

    def queryset(self, request, queryset):
        # On annoté le queryset avec le nombre de films
        queryset = queryset.annotate(nb_films=Count("films"))
        if self.value() == "yes":
            return queryset.filter(nb_films__gt=0)
        elif self.value() == "no":
            return queryset.filter(nb_films=0)
        return queryset
        return queryset

# =========================
# AUTHOR ADMIN
# =========================

@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ("user", "first_name", "last_name", "email","date_naissance", "nb_films", "source")
    list_filter = (HasFilmsFilter, "source")
    search_fields = ("user__username", "user__first_name", "user__last_name", "user__email", "source")
    inlines = [AuthorRatingInlineForAuthor, FilmInline, ]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.annotate(nb_films=Count("films"))

    def nb_films(self, obj):
        return obj.nb_films

    nb_films.admin_order_field = "films"
    
# =========================
# SPECTATOR ADMIN
# =========================

@admin.register(Spectator)
class SpectatorAdmin(admin.ModelAdmin):
    list_display = ("user", "first_name", "last_name", "email", "bio")
    search_fields = ("user__username", "user__first_name", "user__last_name", "user__email")
    inlines = [
        FilmRatingInlineForSpectator,
        AuthorRatingInlineForSpectator,
        FavoriteInline,
    ]


# =========================
# USER ADMIN (principal)
# =========================

@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    list_display = ("username", "email", "is_staff", "is_active")
    search_fields = ("username", "email")
    ordering = ("username",)
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        ("Informations personnelles", {"fields": ("first_name", "last_name", "email")}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Dates importantes", {"fields": ("last_login", "date_joined")}),
    )

