from enum import Enum


class MessageKind(str, Enum):
    COMMAND = "command"  # /진행사항 같은 명령
    RECORD = "record"  # ~일차 완료 기록
    NOOP = "noop"  # 아무 의미 없는 일반 메시지
