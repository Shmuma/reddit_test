import logging


def setup_logging():
    logging.basicConfig(format="%(asctime)-15s %(levelname)s %(name)s %(message)s", level=logging.INFO)
