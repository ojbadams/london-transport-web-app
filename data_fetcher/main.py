from src.loaders import DataExtractor
from src.transformers import DataTransformer
import time, logging, sys

logging.basicConfig(
        stream=sys.stdout,
        level=logging.DEBUG,
        format="%(asctime)s [%(levelname)s] %(message)s"
    )
logger = logging.getLogger(__name__)

def main():
    logger.info("Starting....")
    de = DataExtractor()
    dt = DataTransformer()

    while True:
        logger.info("Running Fetch")
        de.fetch_data()
        dt.transform_bike_dock()
        time.sleep(6)

if __name__ == "__main__":
    print("Starting....")
    main()