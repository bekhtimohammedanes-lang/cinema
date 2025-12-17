import requests
from django.core.management.base import BaseCommand
from django.conf import settings
from cinema_app.models import Film, User, Author
from datetime import datetime

class Command(BaseCommand):
    help = "Import films et auteurs depuis l'API TMDb"

    TMDB_API_URL = "https://api.themoviedb.org/3/movie/popular"
        
    def handle(self, *args, **options):
    
    
        def map_vote_to_evaluation(vote_average):
            if vote_average is None:
                return 3  # valeur par défaut
            # vote_average entre 0 et 10 → scale de 1 à 5
            return max(1, min(5, round(vote_average / 2)))

    
        api_key = settings.TMDB_API_KEY
        self.stdout.write(self.style.WARNING(f"api_key: {api_key}"))
        if not api_key:
            self.stdout.write(self.style.ERROR("TMDB_API_KEY non défini dans les settings"))
            return

        page = 1
        while page <= 2:  # Limite d'exemple à 2 pages
            self.stdout.write(self.style.NOTICE(f"--- Page {page} ---"))

            response = requests.get(
                self.TMDB_API_URL, params={"api_key": api_key, "page": page}
            )
            if response.status_code != 200:
                self.stdout.write(self.style.ERROR(f"Erreur TMDb API: {response.status_code}"))
                break

            data = response.json()
            movies = data.get("results", [])
            total_movies = len(movies)
            self.stdout.write(self.style.NOTICE(f"Nombre de films récupérés: {total_movies}"))

            for index, movie in enumerate(movies, start=1):
                title = movie.get("title")
                self.stdout.write(self.style.NOTICE(f"[{index}/{total_movies}] Traitement du film: {title}"))

                description = movie.get("overview", "")
                release_date_str = movie.get("release_date", None)
                vote_average = movie.get("vote_average", 0)

                # Conversion de la date
                if release_date_str:
                    try:
                        release_date = datetime.strptime(release_date_str, "%Y-%m-%d").date()
                    except ValueError:
                        release_date = None
                else:
                    release_date = None

                # Création ou récupération du film
                film, created = Film.objects.get_or_create(
                    title=title,
                    defaults={
                        "description": description,
                        "release_date": release_date,
                        "status": Film.STATUS_PUBLISHED,
                        "evaluation": map_vote_to_evaluation(vote_average),
                        "source": Film.SOURCE_TMDB,
                    },
                )
                if created:
                    self.stdout.write(self.style.SUCCESS(f"Film importé: {title}"))
                else:
                    self.stdout.write(self.style.WARNING(f"Film déjà existant: {title}"))

                # Récupération des crédits pour obtenir les auteurs
                movie_id = movie.get("id")
                credits_resp = requests.get(
                    f"https://api.themoviedb.org/3/movie/{movie_id}/credits",
                    params={"api_key": api_key},
                )
                if credits_resp.status_code != 200:
                    self.stdout.write(self.style.WARNING(f"Impossible de récupérer les crédits pour: {title}"))
                    continue

                credits = credits_resp.json()
                directors = [c for c in credits.get("crew", []) if c.get("job") == "Director"]
                for crew_member in directors:
                    author_name = crew_member.get("name")
                    username = author_name.replace(" ", "_")
                    user, _ = User.objects.get_or_create(username=username)
                    author, _ = Author.objects.get_or_create(user=user, source= Author.SOURCE_TMDB)
                    film.authors.add(author)
                    self.stdout.write(self.style.SUCCESS(f"    Auteur ajouté: {author_name}"))

            page += 1

        self.stdout.write(self.style.SUCCESS("Import TMDb terminé."))

