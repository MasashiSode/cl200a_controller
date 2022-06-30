import logging
from pathlib import Path


class Logger:

    logger_obj = None

    @classmethod
    def logger(
        cls,
        logger_name="cl200a controller log",
        log_file_path=Path("./cl200a_controller.log"),
        show_debug_message=False,
    ):

        if cls.logger_obj is None:
            cls.logger_obj = cls.__create_logger(
                logger_name=logger_name,
                log_file_path=log_file_path,
                show_debug_message=show_debug_message,
            )
        return cls.logger_obj

    @classmethod
    def __create_logger(cls, logger_name, log_file_path, show_debug_message):
        logger = logging.getLogger(logger_name)

        if show_debug_message:
            logger.setLevel(logging.DEBUG)
        else:
            logger.setLevel(logging.INFO)

        file_handler = logging.FileHandler(log_file_path)
        logger.addHandler(file_handler)

        stream_handler = logging.StreamHandler()
        logger.addHandler(stream_handler)

        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(filename)s - %(funcName)s"
            + " - line: %(lineno)d: %(levelname)s - %(message)s"
        )
        file_handler.setFormatter(formatter)
        stream_handler.setFormatter(formatter)
        return logger

    @classmethod
    def reset_logger(cls):
        cls.logger_obj = None
