import os
import pytest
import logging

from db import Repository

from usecase import MessageHandler

from entities import Errors
from entities import MessageKind
from entities import ProgressSummary
from entities import ClassificationResult


class MockClock:
    def __init__(self, current_day_return):
        self._day = current_day_return

    def current_day(self):
        return self._day


db_path = "./tests/db/test_message_handler.db"

try:
    os.remove(db_path)
    print("file deleted")
except FileNotFoundError:
    print("file not found")

clock = MockClock(current_day_return=4)

repo = Repository(
    db_path, day_counter=clock, logger_stream=True, logging_level=logging.INFO
)

message_handler = MessageHandler(repo, clock)


test_case = [
    ClassificationResult(MessageKind.RECORD, "sender1", "test1", days=[2]),
    ClassificationResult(MessageKind.RECORD, "sender2", "test2", days=[1, 2]),
    ClassificationResult(MessageKind.RECORD, "sender4", "test4", days=[1, 2, 3]),
    ClassificationResult(MessageKind.RECORD, "sender5", "test5", days=[1, 2, 3, 4]),
]

expected = [Errors.SUCCESS] * len(test_case)


@pytest.mark.parametrize("t,e", [(a, b) for a, b in zip(test_case, expected)])
def test_right_date_form(t, e):
    assert message_handler.handle_record_message(t) == e


test_case = [
    ClassificationResult(MessageKind.RECORD, "sender3", "test3", days=[1, 1, 1]),
    ClassificationResult(MessageKind.RECORD, "sender5", "test5", days=[]),
    ClassificationResult(
        MessageKind.RECORD, "sender6", "test6", days=[clock.current_day() + 100]
    ),
    ClassificationResult(MessageKind.RECORD, "sender7", "test7", days=[-1000]),
    ClassificationResult(MessageKind.COMMAND, "sender7", "test7", days=[-1000]),
]

expected = [
    Errors.DB_DUPLICATE_DAY,
    Errors.DATE_ERROR,
    Errors.DATE_ERROR,
    Errors.DATE_ERROR,
    Errors.TYPE_ERROR,
]


@pytest.mark.parametrize("t,e", [(a, b) for a, b in zip(test_case, expected)])
def test_wrong_date_form(t, e):
    assert message_handler.handle_record_message(t) == e


test_case = [
    ClassificationResult(MessageKind.COMMAND, "sender1", "test1", command="/진행상황"),
    ClassificationResult(MessageKind.COMMAND, "sender2", "test2", command="/진행상황"),
    ClassificationResult(MessageKind.COMMAND, "sender3", "test3", command="/진행상황"),
    ClassificationResult(MessageKind.COMMAND, "sender4", "test4", command="/진행상황"),
    ClassificationResult(MessageKind.COMMAND, "sender5", "test5", command="/진행상황"),
]

expected = [
    ProgressSummary("sender1", 1, clock.current_day(), [1, 3, 4]),
    ProgressSummary("sender2", 2, clock.current_day(), [3, 4]),
    ProgressSummary("sender3", 1, clock.current_day(), [2, 3, 4]),
    ProgressSummary("sender4", 3, clock.current_day(), [4]),
    ProgressSummary("sender5", 4, clock.current_day(), []),
]


@pytest.mark.parametrize("t,e", [(a, b) for a, b in zip(test_case, expected)])
def test_right_progress_summary_work(t, e):
    assert message_handler.handle_command_message(t) == e


test_case = [
    ClassificationResult(
        MessageKind.COMMAND, "sender_fake", "test1", command="/진행상황"
    ),
    ClassificationResult(
        MessageKind.COMMAND, "sender_who", "test2", command="/진행상황"
    ),
]

expected = [
    ProgressSummary("sender_fake", 0, clock.current_day(), [1, 2, 3, 4]),
    ProgressSummary("sender_who", 0, clock.current_day(), [1, 2, 3, 4]),
]


@pytest.mark.parametrize("t,e", [(a, b) for a, b in zip(test_case, expected)])
def test_get_user_not_exists(t, e):
    assert message_handler.handle_command_message(t) == e
