import json
from pathlib import Path
from threading import Lock
from typing import Dict


class ContentQueueStore:
    def __init__(self):
        self._lock = Lock()

        # Backend root folder:
        # backend/app/services/content_queue_store.py
        #        ↑
        # parents[2] = backend
        backend_dir = Path(
            __file__
        ).resolve().parents[2]

        # Persistent storage folder
        data_dir = backend_dir / "data"

        data_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        # Persistent queue database
        self._file_path = (
            data_dir / "content_queue.json"
        )

        self._queue: Dict[
            str,
            dict,
        ] = {}

        self._load_queue()

    # ==========================================================
    # LOAD QUEUE FROM DISK
    # ==========================================================

    def _load_queue(self):
        if not self._file_path.exists():
            self._queue = {}
            return

        try:
            with open(
                self._file_path,
                "r",
                encoding="utf-8",
            ) as file:
                data = json.load(file)

            if isinstance(data, dict):
                self._queue = data
            else:
                self._queue = {}

        except (
            json.JSONDecodeError,
            OSError,
        ):
            # Do not crash backend if the
            # queue file is temporarily invalid.
            self._queue = {}

    # ==========================================================
    # SAVE QUEUE TO DISK
    # ==========================================================

    def _save_queue(self):
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
                self._queue,
                file,
                ensure_ascii=False,
                indent=2,
                default=str,
            )

        # Safely replace old queue file
        temp_file.replace(
            self._file_path
        )

    # ==========================================================
    # CREATE QUEUE ITEM
    # ==========================================================

    def create(
        self,
        item: dict,
    ) -> dict:
        with self._lock:
            queue_id = item["queue_id"]

            self._queue[
                queue_id
            ] = item

            self._save_queue()

            return dict(item)

    # ==========================================================
    # GET QUEUE ITEM
    # ==========================================================

    def get(
        self,
        queue_id: str,
    ):
        with self._lock:
            item = self._queue.get(
                queue_id
            )

            return (
                dict(item)
                if item
                else None
            )

    # ==========================================================
    # UPDATE QUEUE ITEM
    # ==========================================================

    def update(
        self,
        queue_id: str,
        **changes,
    ):
        with self._lock:
            item = self._queue.get(
                queue_id
            )

            if not item:
                return None

            item.update(
                changes
            )

            self._save_queue()

            return dict(item)

    # ==========================================================
    # DELETE QUEUE ITEM
    # ==========================================================

    def delete(
        self,
        queue_id: str,
    ) -> bool:
        with self._lock:
            if (
                queue_id
                not in self._queue
            ):
                return False

            del self._queue[
                queue_id
            ]

            self._save_queue()

            return True

    # ==========================================================
    # LIST ALL QUEUE ITEMS
    # ==========================================================

    def list(self):
        with self._lock:
            items = [
                dict(item)
                for item in
                self._queue.values()
            ]

            # Oldest queue item first
            # so Aadwik processes in order.
            items.sort(
                key=lambda item:
                    item.get(
                        "created_at",
                        "",
                    )
            )

            return items

    # ==========================================================
    # COUNT ACTIVE QUEUE ITEMS
    # ==========================================================

    def count_active(self) -> int:
        active_statuses = {
            "WAITING_FOR_STORY",
            "WAITING_FOR_GENERATION",
            "GENERATING",
        }

        with self._lock:
            return sum(
                1
                for item in
                self._queue.values()
                if item.get(
                    "status"
                )
                in active_statuses
            )


# ==========================================================
# GLOBAL CONTENT QUEUE STORE
# ==========================================================

content_queue_store = ContentQueueStore()