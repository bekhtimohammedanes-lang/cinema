from django.contrib.auth.models import AbstractUser
from django.db import models

# =========================
# Modèle principal
# =========================
class User(AbstractUser):
    pass  # Modèle principal pour l'authentification


# =========================
# Authors
# =========================
class Author(models.Model):

    SOURCE_ADMIN = "ADMIN"
    SOURCE_TMDB = "TMDB"

    SOURCE_CHOICES = (
        (SOURCE_ADMIN, "Admin"),
        (SOURCE_TMDB, "TMDb"),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="author_profile")
    date_naissance = models.DateField(null=True, blank=True)
    
    source = models.CharField(max_length=10, choices=SOURCE_CHOICES, default=SOURCE_ADMIN)

    # autres champs spécifiques auteur
    
    @property
    def first_name(self):
        return self.user.first_name

    @property
    def last_name(self):
        return self.user.last_name

    @property
    def email(self):
        return self.user.email

    @property
    def films(self):
        return self.films_set.all()

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username}"

class Spectator(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="spectator_profile")
    bio = models.TextField(blank=True)
    avatar = models.ImageField(upload_to="avatars/", null=True, blank=True)
    # autres champs spécifiques spectateur


    @property
    def first_name(self):
        return self.user.first_name

    @property
    def last_name(self):
        return self.user.last_name

    @property
    def email(self):
        return self.user.email
        

    def __str__(self):
        return self.user.username


# =========================
# Film
# =========================
class Film(models.Model):
    STATUS_DRAFT = "DRAFT"
    STATUS_PUBLISHED = "PUBLISHED"
    STATUS_ARCHIVED = "ARCHIVED"
    
    SOURCE_ADMIN = "ADMIN"
    SOURCE_TMDB = "TMDB"
    
    STATUS_CHOICES = (
        (STATUS_DRAFT, "Brouillon"),
        (STATUS_PUBLISHED, "Publié"),
        (STATUS_ARCHIVED, "Archivé"),
    )

    EVALUATION_CHOICES = (
        (1, "Très mauvais"),
        (2, "Mauvais"),
        (3, "Moyen"),
        (4, "Bon"),
        (5, "Excellent"),
    )

    SOURCE_CHOICES = (
        (SOURCE_ADMIN, "Admin"),
        (SOURCE_TMDB, "TMDb"),
    )
    
    title = models.CharField(max_length=255)
    description = models.TextField()
    release_date = models.DateField()
    evaluation = models.IntegerField(choices=EVALUATION_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_DRAFT)

    authors = models.ManyToManyField(Author, related_name="films", verbose_name="Auteurs",)
    source = models.CharField(max_length=10, choices=SOURCE_CHOICES, default=SOURCE_ADMIN)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


# =========================
# Notes et favoris
# =========================
class FilmRating(models.Model):
    film = models.ForeignKey(Film, on_delete=models.CASCADE, related_name="ratings")
    spectator = models.ForeignKey(Spectator, on_delete=models.CASCADE, related_name="film_ratings")
    note = models.PositiveSmallIntegerField()

    class Meta:
        unique_together = ("film", "spectator")

    def __str__(self):
        return f"{self.spectator} → {self.film} ({self.note})"


class AuthorRating(models.Model):
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name="author_ratings_received")
    spectator = models.ForeignKey(Spectator, on_delete=models.CASCADE, related_name="author_ratings_given")
    note = models.PositiveSmallIntegerField()

    class Meta:
        unique_together = ("author", "spectator")

    def __str__(self):
        return f"{self.spectator} → {self.author} ({self.note})"


class Favorite(models.Model):
    spectator = models.ForeignKey(Spectator, on_delete=models.CASCADE, related_name="favorites")
    film = models.ForeignKey(Film, on_delete=models.CASCADE, related_name="favorited_by")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("spectator", "film")

    def __str__(self):
        return f"{self.spectator} Film favori '{self.film}'"

