from dataclasses import dataclass

from .message_kind import MessageKind


@dataclass
class ClassificationResult:
    kind: MessageKind
    sender: str
    raw: str
    command: str | None = None  # "/진행사항" 같은 명령어 텍스트
    days: list[int] | None = None  # 기록해야 할 일차 리스트
