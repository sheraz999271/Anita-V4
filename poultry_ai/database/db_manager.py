"""SQLite data access layer for poultry management records."""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class PoultryRecord:
    date: str
    flock_size: int
    mortality: int
    feed_used: float
    avg_weight: float
    droppings_status: str
    disease_detected: str


class DatabaseManager:
    """Encapsulates database initialization and CRUD operations."""

    def __init__(self, db_path: str = "poultry_ai.db") -> None:
        self.db_path = Path(db_path)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS poultry_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT NOT NULL,
                    flock_size INTEGER NOT NULL,
                    mortality INTEGER NOT NULL,
                    feed_used REAL NOT NULL,
                    avg_weight REAL NOT NULL,
                    droppings_status TEXT NOT NULL,
                    disease_detected TEXT NOT NULL
                )
                """
            )

    @staticmethod
    def mortality_rate(flock_size: int, mortality: int) -> float:
        return (mortality / flock_size * 100) if flock_size > 0 else 0.0

    @staticmethod
    def feed_conversion_ratio(feed_used: float, avg_weight: float) -> float:
        return (feed_used / avg_weight) if avg_weight > 0 else 0.0

    def create_record(self, record: PoultryRecord) -> int:
        with self._connect() as conn:
            cursor = conn.execute(
                """
                INSERT INTO poultry_records
                (date, flock_size, mortality, feed_used, avg_weight, droppings_status, disease_detected)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    record.date,
                    record.flock_size,
                    record.mortality,
                    record.feed_used,
                    record.avg_weight,
                    record.droppings_status,
                    record.disease_detected,
                ),
            )
            return int(cursor.lastrowid)

    def fetch_all_records(self) -> List[Dict[str, Any]]:
        with self._connect() as conn:
            rows = conn.execute("SELECT * FROM poultry_records ORDER BY date ASC, id ASC").fetchall()
            return [dict(row) for row in rows]

    def update_record(self, record_id: int, record: PoultryRecord) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                UPDATE poultry_records
                SET date=?, flock_size=?, mortality=?, feed_used=?, avg_weight=?,
                    droppings_status=?, disease_detected=?
                WHERE id=?
                """,
                (
                    record.date,
                    record.flock_size,
                    record.mortality,
                    record.feed_used,
                    record.avg_weight,
                    record.droppings_status,
                    record.disease_detected,
                    record_id,
                ),
            )

    def delete_record(self, record_id: int) -> None:
        with self._connect() as conn:
            conn.execute("DELETE FROM poultry_records WHERE id=?", (record_id,))

    def fetch_record(self, record_id: int) -> Optional[Dict[str, Any]]:
        with self._connect() as conn:
            row = conn.execute("SELECT * FROM poultry_records WHERE id=?", (record_id,)).fetchone()
            return dict(row) if row else None
