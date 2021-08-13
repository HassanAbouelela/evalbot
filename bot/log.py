import logging
import os
import sys

import coloredlogs
import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration

from bot import constants


def setup() -> None:
    """Set up loggers."""
    format_string = "%(asctime)s | %(name)s | %(levelname)s | %(message)s"
    root_log = logging.getLogger()

    if "COLOREDLOGS_LEVEL_STYLES" not in os.environ:
        coloredlogs.DEFAULT_LEVEL_STYLES = {
            **coloredlogs.DEFAULT_LEVEL_STYLES,
            "critical": {"background": "red"},
            "debug": coloredlogs.DEFAULT_LEVEL_STYLES["info"]
        }

    if "COLOREDLOGS_LOG_FORMAT" not in os.environ:
        coloredlogs.DEFAULT_LOG_FORMAT = format_string

    coloredlogs.install(level=logging.DEBUG, logger=root_log, stream=sys.stdout)

    root_log.setLevel(logging.DEBUG if constants.DEBUG_MODE else logging.INFO)
    logging.getLogger("discord").setLevel(logging.WARNING)
    logging.getLogger("websockets").setLevel(logging.WARNING)
    logging.getLogger("chardet").setLevel(logging.WARNING)

    # Set back to the default of INFO even if asyncio's debug mode is enabled.
    logging.getLogger("asyncio").setLevel(logging.INFO)

    _set_debug_loggers()


def setup_sentry() -> None:
    """Set up the Sentry logging integrations."""
    sentry_logging = LoggingIntegration(
        level=logging.DEBUG,
        event_level=logging.WARNING
    )

    sentry_sdk.init(
        dsn=constants.sentry_dsn,
        integrations=[
            sentry_logging
        ],
        release=f"bot@{constants.GIT_SHA}"
    )


def _set_debug_loggers() -> None:
    """
    Set loggers to the debug level according to the value from the LOG_LEVEL env var.

    When the env var is a list of logger names delimited by a comma,
    each of the listed loggers will be set to the debug level.

    If this list is prefixed with a "!", all of the loggers except the listed ones will be set to the debug level.

    Otherwise if the env var begins with a "*",
    the root logger is set to the debug level and other contents are ignored.
    """
    level_filter = constants.log_filter
    if level_filter:
        if level_filter.startswith("*"):
            logging.getLogger().setLevel(logging.DEBUG)

        elif level_filter.startswith("!"):
            logging.getLogger().setLevel(logging.DEBUG)
            for logger_name in level_filter.strip("!,").split(","):
                logging.getLogger(logger_name).setLevel(logging.DEBUG)

        else:
            for logger_name in level_filter.strip(",").split(","):
                logging.getLogger(logger_name).setLevel(logging.DEBUG)
