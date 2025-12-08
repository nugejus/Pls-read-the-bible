# usecase/message_handler.py

import logging

from utilities import set_logger
from utilities import is_valid_command
from utilities import AbsoluteDayCounter

from entities import Errors
from entities import Commands
from entities import MessageKind
from entities import ProgressSummary
from entities import ClassificationResult

from db.repository import Repository


class MessageHandler:
    def __init__(self, repo: Repository, clock: AbsoluteDayCounter) -> None:
        self.repo: Repository = repo
        self.clock: AbsoluteDayCounter = clock
        self.logger: logging.Logger = set_logger(
            "msg_handler", s=True, level=logging.WARNING
        )

    def handle_record_message(self, data: ClassificationResult) -> Errors:
        if data.kind != MessageKind.RECORD:
            self.logger.error(
                "The message must have the MessageKind.RECORD type, got {%s}", data.kind
            )
            return Errors.TYPE_ERROR

        if len(data.days) < 1:
            self.logger.warning("The days is empty")
            return Errors.DATE_ERROR

        if max(data.days) > self.clock.current_day() or min(data.days) <= 0:
            self.logger.warning("The day <= 0 or day > current day")
            return Errors.DATE_ERROR

        for (
            day
        ) in data.days:  # days는 무조건 명시적으로 [몇일차, 몇일차, 몇일차] 로 들어옴
            status = self.repo.post_progress(data.sender, data.raw, day)
            if status == Errors.DB_DUPLICATE_DAY:
                continue
            if status != Errors.SUCCESS:
                return status

        return status

    def handle_command_message(
        self, data: ClassificationResult
    ) -> Errors | ProgressSummary:
        if data.kind != MessageKind.COMMAND:
            self.logger.error(
                "The message must have the MessageKind.COMMAND type, got {%s}",
                data.kind,
            )
            return Errors.TYPE_ERROR

        if not is_valid_command(data.command):
            self.logger.info("The command is wrong, got {%s}", data.command)
            return Errors.WRONG_COMMAND_ERROR

        cmd = Commands(data.command.lstrip("/"))
        if cmd == Commands.PROGRESS_ONE:
            return self.repo.get_progress(sender=data.sender)

        if cmd == Commands.PROGRESS_ALL:
            return self.repo.get_all_progresses()

    def handle_message(self, data: ClassificationResult) -> Errors | ProgressSummary:
        if data.kind == MessageKind.RECORD:
            result = self.handle_record_message(data)
        elif data.kind == MessageKind.COMMAND:
            result = self.handle_command_message(data)
        else:
            if data.kind != MessageKind.NOOP:
                self.logger.error("The message kind %s could not be solved", data.kind)
            result = Errors.TYPE_ERROR

        return result
