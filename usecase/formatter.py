from entities import Errors
from entities import ClassificationResult
from entities import ProgressSummary


class Formatter:
    def __init__(self):
        pass

    def send_to_sever(self, msg):
        pass

    def _compress_day_list(self, days: list[int]) -> list[tuple[int, ...]]:
        if len(days) < 3:
            return [(d,) for d in sorted(days)]

        days = sorted(days)
        result = []

        start = days[0]
        last = days[0]

        for d in days[1:]:
            if d == last + 1:
                last = d
            else:
                # range 완료
                if start != last:
                    result.append((start, last))
                else:
                    result.append((start,))
                start = d
                last = d

        # 마지막 구간 추가
        if start != last:
            result.append((start, last))
        else:
            result.append((start,))

        return result

    def _format_compressed_days(self, days: list[tuple[int, ...]]) -> str:
        parts = []
        for day in days:
            if len(day) == 1:
                parts.append(str(day[0]))
            else:
                s, e = day
                parts.append(f"{s}-{e}")
        return "[" + ", ".join(parts) + "]"

    def send_to_kakao_api_one_sender(self, msg: ProgressSummary | Errors) -> dict[str,list[str]]:
        if isinstance(msg, Errors):
            return ""

        days = self._compress_day_list(msg.missing_days)
        percentage = round(msg.completed_count/msg.max_day * 100,1)

        out_info = [
            f"{self._pad_crown(msg.sender,percentage)}님의 진행상황",
            f"{msg.completed_count}/{msg.max_day} 완료({percentage}%)",
        ]

        if days:
            out_info.append(f"{self._format_compressed_days(days)}를 놓쳤습니다.")

        return {"msg":out_info}

    def send_to_kakao_api_all_senders(
        self, messages: list[ProgressSummary] | Errors
    ) -> dict[str,list[str]]:
        out = []
        for msg in messages:
            percentage = round(msg.completed_count/msg.max_day * 100,1)
            out_info = f"{self._pad_crown(msg.sender,percentage)}:{msg.completed_count}/{msg.max_day}({percentage}%)"
            out.append(out_info)

        return {"msg":out}

    def _pad_crown(self, name, percentage):
        if percentage > 99.99:
            return "👑" + name
        else:
            return name