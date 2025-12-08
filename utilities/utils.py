import logging

from entities import Commands


def is_valid_command(command: str) -> bool:
    cmd = command.strip().lstrip("/")
    try:
        Commands(cmd)
        return True
    except ValueError:
        return False


def set_logger(name: str, s: bool, level: logging = logging.DEBUG) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # 중복 핸들러 방지
    if logger.handlers:
        return logger

    # 1) FILE HANDLER 추가 (name.log)
    log_filename = f"./logs/{name}.log"
    file_handler = logging.FileHandler(log_filename, encoding="utf-8")
    file_handler.setLevel(level)
    file_handler.setFormatter(
        logging.Formatter("%(asctime)s\t%(levelname)-8s\t%(name)-12s\t%(message)s")
    )
    logger.addHandler(file_handler)

    # 2) STREAM HANDLER(s=True일 때만)
    if s:
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(level)
        stream_handler.setFormatter(
            logging.Formatter(
                "[STDOUT] %(asctime)s\t%(levelname)-8s\t%(name)-12s\t%(message)s"
            )
        )
        logger.addHandler(stream_handler)

    # 자녀 로거가 부모로 전달되는 것 방지 (필요하면 켜기)
    logger.propagate = False

    return logger
