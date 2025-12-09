import logging

from flask import Flask

from config import DB_PATH, TOTAL_DAYS, START_DATE

from db import Repository

from .routes import init_app

from usecase import Formatter
from usecase import MessageHandler
from usecase import MessageClassifier

from utilities import DayParser
from utilities import AbsoluteDayCounter


def create_flask_app():
    app = Flask(__name__)
    app.config["JSON_AS_ASCII"] = False

    clock = AbsoluteDayCounter(start_date=START_DATE, tz_offset_hours=3)

    repo = Repository(
        db_path=DB_PATH,
        day_counter=clock,
        total_days=TOTAL_DAYS,
        logger_stream=True,
        logging_level=logging.WARNING,
    )

    handler = MessageHandler(repo, clock)

    parser = DayParser()
    classifer = MessageClassifier(parser)

    formatter = Formatter()

    app.config["CLASSIFIER"] = classifer
    app.config["HANDLER"] = handler
    app.config["FORMATTER"] = formatter

    init_app(app)

    return app
