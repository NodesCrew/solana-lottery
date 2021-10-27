# coding: utf-8

# -*- coding: utf-8 -*-
"""
"""
import config
import logging


def get_logger(name):
    logger = logging.getLogger(name)
    if not logger.handlers:
        formatter = logging.Formatter(u"%(asctime)s [%(process)d] "
                                      u"%(levelname)s %(message)s\n")
        log_handler = logging.FileHandler(config.DIR_LOGS + "/%s.log" % name)
        log_handler.setFormatter(formatter)
        log_handler.setLevel(logging.DEBUG)
        logger.addHandler(log_handler)

        log_handler = logging.StreamHandler()
        log_handler.setFormatter(formatter)
        log_handler.setLevel(logging.DEBUG)
        logger.addHandler(log_handler)

        logger.setLevel(logging.DEBUG)
    return logger
