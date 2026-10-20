import json
from pathlib import Path
from threading import Lock
from typing import Dict


class MovieStore:
    def __init__(self):
        self._lock = Lock()

        # Backend root folder:
        # backend/app/services/movie_store.py
        #        ↑
        # parents[2] = backend
        backend_dir = Path(__file__).resolve().parents[2]

        # Persistent storage folder
        data_dir = backend_dir / "data"
        data_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        # Persistent movie database file
        self._file_path = (
            data_dir / "movies.json"
        )

        self._movies: Dict[
            str,
            dict,
        ] = {}

        self._load_movies()

    # ==========================================================
    # LOAD MOVIES FROM DISK
    # ==========================================================

    def _load_movies(self):
        if not self._file_path.exists():
            self._movies = {}
            return

        try:
            with open(
                self._file_path,
                "r",
                encoding="utf-8",
            ) as file:
                data = json.load(file)

            if isinstance(data, dict):
                self._movies = data
            else:
                self._movies = {}

        except (
            json.JSONDecodeError,
            OSError,
        ):
            # Do not crash the backend if the
            # database file is temporarily invalid.
            self._movies = {}

    # ==========================================================
    # SAVE MOVIES TO DISK
    # ==========================================================

    def _save_movies(self):
        temp_file = (
            self._file_path.with_suffix(
                ".tmp"
            )
        )

        with open(
            temp_file,
            "w",
            encoding="utf-8",
        ) as file:
            json.dump(
                self._movies,
                file,
                ensure_ascii=False,
                indent=2,
                default=str,
            )

        # Replace old file safely
        temp_file.replace(
            self._file_path
        )

    # ==========================================================
    # CREATE MOVIE
    # ==========================================================

    def create(
        self,
        movie: dict,
    ) -> dict:
        with self._lock:
            self._movies[
                movie["movie_id"]
            ] = movie

            self._save_movies()

            return dict(movie)

    # ==========================================================
    # GET MOVIE
    # ==========================================================

    def get(
        self,
        movie_id: str,
    ):
        with self._lock:
            movie = self._movies.get(
                movie_id
            )

            return (
                dict(movie)
                if movie
                else None
            )

    # ==========================================================
    # UPDATE MOVIE
    # ==========================================================

    def update(
        self,
        movie_id: str,
        **changes,
    ):
        with self._lock:
            movie = self._movies.get(
                movie_id
            )

            if not movie:
                return None

            movie.update(
                changes
            )

            self._save_movies()

            return dict(movie)

    # ==========================================================
    # LIST MOVIES
    # ==========================================================

    def list(self):
        with self._lock:
            movies = [
                dict(movie)
                for movie in
                self._movies.values()
            ]

            # Newest movie first
            movies.sort(
                key=lambda movie:
                    movie.get(
                        "created_at",
                        "",
                    ),
                reverse=True,
            )

            return movies


# Global movie store
store = MovieStore()