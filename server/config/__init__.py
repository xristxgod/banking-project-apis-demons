import logging


def get_logger(name: str):
    logger = logging.getLogger(name)

    logger.setLevel(logging.INFO)

    if len(logger.handlers) < 1:
        info_format = logging.Formatter(f"%(asctime)s :: %(levelname)s :: {name}\n%(message)s\n----------------")
        error_format = info_format
        warning_format = info_format
        debug_format = info_format

        handler_error = logging.StreamHandler()
        handler_error.setLevel(logging.ERROR)
        handler_error.setFormatter(error_format)

        handler_info = logging.StreamHandler()
        handler_info.setLevel(logging.INFO)
        handler_info.setFormatter(info_format)

        handler_warning = logging.StreamHandler()
        handler_warning.setLevel(logging.WARNING)
        handler_warning.setFormatter(warning_format)

        handler_debug = logging.StreamHandler()
        handler_debug.setLevel(logging.DEBUG)
        handler_debug.setFormatter(debug_format)

        logger.addHandler(handler_error)
        logger.addHandler(handler_info)

    return logger
