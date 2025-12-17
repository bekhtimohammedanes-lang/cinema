from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import (
    Author,
    Spectator,
    Film,
    FilmRating,
    AuthorRating,
    Favorite,
)

User = get_user_model()

# =====================================================
# USER
# =====================================================

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
        )


# =====================================================
# AUTHOR
# =====================================================

class FilmLightSerializer(serializers.ModelSerializer):
    class Meta:
        model = Film
        fields = (
            "id",
            "title",
            "status",
            "evaluation",
        )


class AuthorSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    films = FilmLightSerializer(many=True, read_only=True)

    class Meta:
        model = Author
        fields = (
            "id",
            "user",
            "date_naissance",
            "films",
        )


# =====================================================
# SPECTATOR
# =====================================================

class SpectatorSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Spectator
        fields = (
            "id",
            "user",
            "bio",
            "avatar",
        )


# =====================================================
# FILM
# =====================================================

class AuthorLightSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Author
        fields = (
            "id",
            "user",
        )


class FilmSerializer(serializers.ModelSerializer):
    authors = AuthorLightSerializer(many=True, read_only=True)

    class Meta:
        model = Film
        fields = (
            "id",
            "title",
            "description",
            "release_date",
            "evaluation",
            "status",
            "authors",
        )


class FilmWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Film
        fields = (
            "title",
            "description",
            "release_date",
            "evaluation",
            "status",
            "authors",
        )


# =====================================================
# RATINGS
# =====================================================

class FilmRatingSerializer(serializers.ModelSerializer):
    spectator = SpectatorSerializer(read_only=True)

    class Meta:
        model = FilmRating
        fields = (
            "id",
            "note",
            "spectator",
        )


class AuthorRatingSerializer(serializers.ModelSerializer):
    spectator = SpectatorSerializer(read_only=True)

    class Meta:
        model = AuthorRating
        fields = (
            "id",
            "note",
            "spectator",
        )


# =====================================================
# FAVORITES
# =====================================================

class FavoriteSerializer(serializers.ModelSerializer):
    film = FilmLightSerializer(read_only=True)

    class Meta:
        model = Favorite
        fields = (
            "id",
            "film",
            "created_at",
        )


# =====================================================
# SPECTATOR REGISTER
# =====================================================

class SpectatorRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = (
            "username",
            "email",
            "password",
            "first_name",
            "last_name",
        )

    def create(self, validated_data):
        password = validated_data.pop("password")

        user = User.objects.create_user(
            password=password,
            **validated_data
        )

        Spectator.objects.create(user=user)
        return user

