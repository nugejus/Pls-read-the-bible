# utilities/day_parser.py

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Callable, List, Pattern, Match

DayList = List[int]
ParseFn = Callable[[Match[str]], DayList]


@dataclass(frozen=True)
class DayParseRule:
    """
    하나의 패턴 룰:
    - name: 디버깅/로그용 이름
    - pattern: 정규식
    - handler: 매칭된 Match -> [day, ...] 로 바꿔주는 함수
    """

    name: str
    pattern: Pattern[str]
    handler: ParseFn


def _handle_range(match: Match[str]) -> DayList:
    start = int(match.group(1))
    end = int(match.group(2))
    if start > end:
        start, end = end, start
    return list(range(start, end + 1))


def _handle_single(match: Match[str]) -> DayList:
    return [int(match.group(1))]


def _handle_list(match: Match[str]) -> DayList:
    raw = match.group(1)
    result: DayList = []
    for part in raw.split(","):
        part = part.strip()
        if not part:
            continue
        try:
            result.append(int(part))
        except ValueError:
            continue
    return result


def _handle_mixed(match: Match[str]) -> DayList:
    """
    "332, 334-339, 341" / "1-3, 5" 같이
    단일 + 구간이 섞인 표현을 처리.
    """
    expr = match.group(1)
    result: DayList = []

    for token in expr.split(","):
        token = token.strip()
        if not token:
            continue

        # 구간: 334-339, 1~3 등
        m_range = re.fullmatch(r"(\d+)\s*[-~]\s*(\d+)", token)
        if m_range:
            start = int(m_range.group(1))
            end = int(m_range.group(2))
            if start > end:
                start, end = end, start
            result.extend(range(start, end + 1))
            continue

        # 단일: 332, 341, 5 등
        m_single = re.fullmatch(r"(\d+)", token)
        if m_single:
            result.append(int(m_single.group(1)))
            continue

        # 이상한 토큰은 무시
    return result


class DayParser:
    """
    텍스트에서 'N일차 완료' / 'N-M일차 완료' 같은 패턴을 찾아
    [N, ..., M] 리스트로 반환하는 파서.
    """

    def __init__(self, rules: List[DayParseRule] | None = None) -> None:
        # 사용자가 커스텀 룰을 넣을 수도 있고,
        # 안 넣으면 기본 룰을 사용.
        self._rules: List[DayParseRule] = rules or self._default_rules()

    def parse(self, text: str) -> DayList:
        """
        매칭되면 해당 룰의 handler 결과를 리턴,
        아무 것도 매칭 안 되면 [] 리턴.
        """
        for rule in self._rules:
            m = rule.pattern.search(text)
            if m:
                return rule.handler(m)
        return []

    @staticmethod
    def _default_rules() -> List[DayParseRule]:
        """
        기본 제공 룰들.
        여기만 수정하면 패턴을 쉽게 추가/변경 가능.
        - 완료/클리어 둘 다 허용
        - '일차'와 완료 단어 사이에 임의 텍스트 허용
        """
        return [
            # 혼합 패턴: 332, 334-339, 341(일차) 완료 / 1-3, 5(일차) 완료 등
            DayParseRule(
                name="mixed_days_complete",
                pattern=re.compile(
                    r"((?:\d+(?:\s*[-~]\s*\d+)?)(?:\s*,\s*\d+(?:\s*[-~]\s*\d+)?)*?)"
                    r"(?:\s*일차)?(?:[^\n\r]*?)(?:완료|클리어)"
                ),
                handler=_handle_mixed,
            ),
            # 1,3,4(일차) 완료 / 2,5,6,7 (일차) 클리어
            DayParseRule(
                name="list_days_complete",
                pattern=re.compile(
                    r"(?:^|\s)(\d+(?:\s*,\s*\d+)*)"
                    r"(?:\s*일차)?(?:[^\n\r]*?)(?:완료|클리어)"
                ),
                handler=_handle_list,
            ),
            # 1-3(일차) 완료 / 1~5(일차) 통독 완료
            DayParseRule(
                name="range_day_complete",
                pattern=re.compile(
                    r"(\d+)\s*[-~]\s*(\d+)" r"(?:\s*일차)?(?:[^\n\r]*?)(?:완료|클리어)"
                ),
                handler=_handle_range,
            ),
            # 1(일차) 완료 / 1(일차) 통독 완료 / 성경읽기 1(일차) 클리어
            DayParseRule(
                name="single_day_complete",
                pattern=re.compile(r"(\d+)(?:\s*일차)?(?:[^\n\r]*?)(?:완료|클리어)"),
                handler=_handle_single,
            ),
        ]
