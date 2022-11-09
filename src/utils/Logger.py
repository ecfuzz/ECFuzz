import logging
import os
import sys

from utils import UnitConstant


def getLogger():
    """(Facade)get the logger instance. Which is designed by single pattern.

    Returns:
        logging.Logger: the logger instance
    """
    return Logger.get_logger()


class Logger(object):
    # a static member of 'Logger' class
    logger = None

    def __init__(self) -> None:
        pass

    @staticmethod
    def get_logger() -> logging.Logger:
        """get the logger instance. Which is designed by single pattern.

        Returns:
            logging.Logger: the logger instance
        """
        # return 'logger' if it exists
        if Logger.logger is None:
            # create a new log file in current working path
            log_dir = UnitConstant.FUZZER_DIR

            log_path = os.path.join(log_dir, 'fuzzer.log')

            # remove the previous one if it exists
            if os.path.exists(log_path):
                try:
                    os.remove(log_path)
                except Exception:
                    pass

            # some initialization work
            logging.basicConfig(
                level=logging.INFO,
                format='[%(asctime)s-%(levelname)s-%(pathname)s-%(funcName)s:%(lineno)d]\n%(message)s',
                datefmt="%Y-%m-%d %H:%M:%S",
                filename=log_path,
                filemode='w'
            )

            # create an instance from library 'logging'
            Logger.logger = logging.getLogger()
        return Logger.logger

    @staticmethod
    def info(msg: str):
        Logger.get_logger().info(msg)

    @staticmethod
    def warning(msg: str):
        Logger.get_logger().warning(msg)

    @staticmethod
    def error(msg: str):
        Logger.get_logger().error(msg)
