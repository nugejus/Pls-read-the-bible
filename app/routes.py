from flask import request, jsonify, current_app

from usecase import Formatter
from usecase import MessageHandler
from usecase import MessageClassifier


def init_app(app):
    @app.route("/", methods=["POST"])
    def handle_message():
        data = request.get_json(force=True, silent=True) or {}

        classifier: MessageClassifier = current_app.config["CLASSIFIER"]
        handler: MessageHandler = current_app.config["HANDLER"]
        formatter: Formatter = current_app.config["FORMATTER"]

        message = classifier.classify(data)

        progress = handler.handle_message(message)

        reply: dict[str, list[str]]

        if isinstance(progress, list):
            reply = formatter.send_to_kakao_api_all_senders(progress)
        else:
            reply = formatter.send_to_kakao_api_one_sender(progress)

        # Kakao / 외부 API가 원하는 형식으로 응답
        return jsonify(reply)
