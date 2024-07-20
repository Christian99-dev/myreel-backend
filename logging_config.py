import logging

class MyFilter(logging.Filter):
    def __init__(self, level):
        self.__level = level

    def filter(self, logRecord):
        return logRecord.levelno <= self.__level

def setup_logging_testing():
    logging.basicConfig(level=logging.DEBUG)
    logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)
    logging.getLogger('asyncio').setLevel(logging.INFO)
    logging.getLogger("httpx").setLevel(logging.WARNING)    
    logger = logging.getLogger("testing")
    logger.setLevel(logging.DEBUG)
    logger.addFilter(MyFilter(logging.DEBUG))

def setup_logging_prod():
    access_logger = logging.getLogger("access")
    access_logger.setLevel(logging.INFO)
    file_handler = logging.FileHandler('access.log')
    access_logger.addHandler(file_handler)

    debug_logger = logging.getLogger("prod_debug")
    debug_logger.setLevel(logging.DEBUG)    
