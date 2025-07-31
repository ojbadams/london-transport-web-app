import logging
import sys
import time

from src.loaders import DataExtractor
from src.transformers import DataTransformer

logging.basicConfig(
    stream=sys.stdout,
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)


def main():
    logger.info("Starting....")
    de = DataExtractor()
    counter = 0

    while True:
        print(f"running counter {counter}")
        de.refresh()
        counter += 1

if __name__ == "__main__":
    print("Starting....")
    main()
