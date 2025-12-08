# usecases/classifier.py

import logging

from typing import Dict

from entities import ClassificationResult
from entities import MessageKind

from utilities import DayParser
from utilities import set_logger


class MessageClassifier:
    """
    외부 API에서 들어온 raw 데이터를 받아서
    - COMMAND (/로 시작하는 명령)
    - RECORD  (~일차 완료 메시지)
    - NOOP    (위 둘에 해당 안 되는 일반 대화)
    로 분류하는 책임을 가진 클래스.
    """

    def __init__(self, parser: DayParser) -> None:
        self.parser: DayParser = parser
        self.logger: logging = set_logger("classifier", s=True, level=logging.DEBUG)

    def classify(self, raw: Dict[str, str]) -> ClassificationResult:
        """
        raw: {"sender": ..., "msg": ...}
        """
        msg = (raw.get("msg") or "").strip()
        sender = raw.get("sender", "").strip()

        # 1) 명령 메시지: "/..." 로 시작
        if msg.startswith("/"):
            return ClassificationResult(
                kind=MessageKind.COMMAND,
                sender=sender,
                raw=raw.get("msg", ""),
                command=msg,
            )

        # 2) 기록 메시지: "~일차 완료" 패턴
        days = self.parser.parse(msg)
        if days:
            return ClassificationResult(
                kind=MessageKind.RECORD,
                sender=sender,
                raw=raw.get("msg", ""),
                days=days,
            )

        self.logger.debug(
            "The message failed to parse, message = {%s}", raw.get("msg", "")
        )
        # 3) 그 외는 의미 없는 일반 메시지
        return ClassificationResult(
            kind=MessageKind.NOOP,
            sender=sender,
            raw=raw["msg"],
        )
