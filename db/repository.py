# db.py
import sqlite3
import logging

from utilities import set_logger
from utilities import AbsoluteDayCounter

from entities import Errors
from entities import ProgressSummary


class Repository:
    def __init__(
        self,
        db_path: str,
        day_counter: AbsoluteDayCounter,
        total_days: int = 365,
        logger_stream: bool = False,
        logging_level: logging = logging.DEBUG,
    ) -> None:

        self.db_path = db_path
        self.day_counter = day_counter
        self.logger = set_logger("db", logger_stream, logging_level)

        with self._get_connection() as conn:
            cursor: sqlite3.Cursor = conn.cursor()
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS reading_plan(
                    day INTEGER PRIMARY KEY
                )
                """
            )

            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS raw_messages(
                    id      INTEGER PRIMARY KEY AUTOINCREMENT,
                    sender  TEXT NOT NULL,
                    msg     TEXT NOT NULL,
                    time    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            )

            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS progress(
                    id      INTEGER PRIMARY KEY AUTOINCREMENT,
                    sender  TEXT NOT NULL,
                    day     INTEGER NOT NULL,
                    msg_id  INTEGER,
                    time    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(sender, day)
                )
                """
            )

            cursor.executemany(
                "INSERT OR IGNORE INTO reading_plan(day) VALUES (?)",
                [(d,) for d in range(1, total_days + 1)],
            )

    def _get_connection(self) -> sqlite3.Connection:
        """
        make connection with database
        """

        connection = sqlite3.connect(self.db_path)
        connection.row_factory = sqlite3.Row
        return connection

    def _post_raw(self, sender: str, raw: str) -> Errors | int:

        with self._get_connection() as conn:
            try:
                cursor: sqlite3.Cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT INTO raw_messages(
                        sender, msg
                    ) VALUES (?,?)
                    """,
                    (sender, raw),
                )

                msg_id = cursor.lastrowid

            except Exception as e:
                self.logger.error(
                    "Failed to post in raw_messages table sender:%s, error:%s",
                    sender,
                    e,
                )
                return Errors.DB_FAIL
        self.logger.debug(
            "The raw information has been posted msg_id:%s sender:%s, message:%s",
            msg_id,
            sender,
            raw,
        )
        return msg_id

    def post_progress(self, sender: str, raw: str, day: int) -> Errors:
        msg_id = self._post_raw(sender, raw)

        with self._get_connection() as conn:
            try:
                cursor: sqlite3.Cursor = conn.cursor()

                cursor.execute(
                    """
                    INSERT INTO progress(
                        sender, day, msg_id
                    ) VALUES (?,?,?)
                    """,
                    (sender, day, msg_id),
                )
            except sqlite3.IntegrityError:
                # UNIQUE(sender, day) 위반 → 이미 그 day는 등록됨
                self.logger.warning(
                    "Duplicated progress ignored sender:%s, day:%s", sender, day
                )
                return Errors.DB_DUPLICATE_DAY

            except Exception as e:
                self.logger.error(
                    "Failed to post in progress table sender:%s, days:%s, error:%s",
                    sender,
                    day,
                    e,
                )
                return Errors.DB_FAIL

        self.logger.info(
            "The progress posted successfully, sender:%s, days:%s", sender, day
        )
        return Errors.SUCCESS

    def get_progress(self, sender: str) -> ProgressSummary | Errors:

        with self._get_connection() as conn:
            try:
                cursor: sqlite3.Cursor = conn.cursor()

                cursor.execute(
                    """
                    SELECT 
                    COUNT(*) as completed
                    FROM progress
                    WHERE sender = ?
                    """,
                    (sender,),
                )

                row = cursor.fetchone()
                completed = (
                    row["completed"] if row and row["completed"] is not None else 0
                )

                max_day = self.day_counter.current_day()

                cursor.execute(
                    """
                    SELECT r.day 
                    FROM reading_plan AS r
                    LEFT JOIN progress as p 
                    ON p.sender = ?
                    AND r.day = p.day
                    WHERE r.day <= ?
                    AND p.day IS NULL
                    ORDER BY r.day
                    """,
                    (sender, max_day),
                )
                missing_days = [int(r["day"]) for r in cursor.fetchall()]
            except Exception as e:
                self.logger.error(
                    "Failed to get from progress table sender:%s, error:%s", sender, e
                )
                return Errors.DB_FAIL

        return ProgressSummary(
            sender=sender,
            completed_count=completed,
            max_day=max_day,
            missing_days=missing_days,
        )

    def get_all_progresses(self) -> list[ProgressSummary] | Errors:
        with self._get_connection() as conn:
            try:
                cursor: sqlite3.Cursor = conn.cursor()

                cursor.execute(
                    """
                    SELECT 
                        sender,
                        COUNT(*) as completed
                    FROM progress
                    GROUP BY sender
                    ORDER BY sender
                    """
                )

                progresses = []
                rows = cursor.fetchall()
                max_day = self.day_counter.current_day()
                for row in rows:
                    sender = row["sender"]
                    completed = row["completed"]

                    prog = ProgressSummary(sender, completed, max_day, [])

                    progresses.append(prog)

            except Exception as e:
                self.logger.error("Failed to get from progress table error:%s", e)
                return Errors.DB_FAIL

        return progresses
