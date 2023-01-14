import logging

FORMAT = "[%(levelname)s]: %(message)s  [%(filename)s:%(lineno)d]"
logging.basicConfig(level=logging.INFO, format=FORMAT)

logger = logging.getLogger("rich")
