from dataclasses import dataclass


@dataclass
class ProgressSummary:
    sender: str
    completed_count: int
    max_day: int
    missing_days: list[int]
