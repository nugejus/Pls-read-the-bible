from datetime import datetime, date, timezone, timedelta


class AbsoluteDayCounter:
    def __init__(self, start_date: date, tz_offset_hours: int = 9):
        """
        start_date: 기준 시작일 (예: date(2025, 1, 1))
        tz_offset_hours: 한국은 UTC+9, 러시아는 UTC+3 등
        """
        self.start_date = start_date
        self.tz = timezone(timedelta(hours=tz_offset_hours))

    def _today(self) -> date:
        """온라인 절대 날짜 (UTC 기반 + 오프셋 반영)"""
        return datetime.now(self.tz).date()

    def current_day(self) -> int:
        """
        오늘이 시작일부터 몇 번째 날인지 계산
        Day 1 = start_date
        """
        delta = self._today() - self.start_date
        return delta.days + 1  # 첫 날을 1로 두기 위해 +1
