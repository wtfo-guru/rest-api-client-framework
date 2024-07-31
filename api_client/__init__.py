"""
__init__ module for the package api_client of rest-api-client-framework library.

Variables:
    logger
"""

import logging
import os


def _create_library_logger() -> logging.Logger:
    library = "rest-api-client-framework"
    log_name = "{0}-{1}".format(library, __name__)
    env_level = os.getenv("REST_API_CLIENT_FRAMEWORK_LOG_LEVEL", "WARNING").upper()
    if env_level == "DEBUG":
        level = logging.DEBUG
    elif env_level == "INFO":
        level = logging.INFO
    else:
        level = logging.WARNING
    logging.basicConfig(level=level)
    package_logger = logging.getLogger(log_name)
    # print("created log: {0}".format(log_name))
    package_logger.debug("created log: {0}".format(log_name))
    # package_logger.addHandler(logging.NullHandler())
    return package_logger


def _get_logger() -> logging.Logger:
    _create_library_logger()
    if not logging.getLogger().hasHandlers():
        return _create_library_logger()
    return logging.getLogger()


logger = _get_logger()
