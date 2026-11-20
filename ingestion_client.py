

import time
import logging
import requests

from requests.exceptions import (
    ReadTimeout,
    ConnectionError,
    RequestException
)

from loader import load_orders


# --------------------------------------------------
# CONFIGURATION
# --------------------------------------------------

BASE_URL = "http://127.0.0.1:8001/orders"

MAX_RETRIES = 3
REQUEST_TIMEOUT = 30

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger(__name__)


# --------------------------------------------------
# FETCH ONE PAGE WITH RETRY
# --------------------------------------------------

def fetch_page(page, session):
    """
    Fetch one API page.
    Handles rate limits, timeouts and connection errors.
    """

    for attempt in range(1, MAX_RETRIES + 1):

        try:
            logger.info(
                f"Requesting page {page}, "
                f"attempt {attempt}/{MAX_RETRIES}"
            )

            response = session.get(
                BASE_URL,
                params={"page": page},
                timeout=REQUEST_TIMEOUT
            )

            # Handle API rate limiting
            if response.status_code == 429:

                retry_after = response.headers.get("Retry-After")

                wait_time = (
                    float(retry_after)
                    if retry_after
                    else 2 ** (attempt - 1)
                )

                logger.warning(
                    f"HTTP 429 on page {page}. "
                    f"Waiting {wait_time} seconds."
                )

                if attempt == MAX_RETRIES:
                    raise RuntimeError(
                        f"Rate limit retries exhausted for page {page}"
                    )

                time.sleep(wait_time)
                continue

            # Raise error for other HTTP failures
            response.raise_for_status()

            result = response.json()

            logger.info(
                f"Successfully fetched page {page}"
            )

            return result

        except ReadTimeout:

            logger.warning(
                f"Read timeout on page {page}, "
                f"attempt {attempt}/{MAX_RETRIES}"
            )

        except ConnectionError:

            logger.warning(
                f"Connection error on page {page}, "
                f"attempt {attempt}/{MAX_RETRIES}"
            )

        except RequestException:

            logger.exception(
                f"HTTP request failed on page {page}"
            )
            raise

        if attempt < MAX_RETRIES:

            wait_time = 2 ** (attempt - 1)

            logger.info(
                f"Retrying page {page} after "
                f"{wait_time} seconds."
            )

            time.sleep(wait_time)

    raise RuntimeError(
        f"Unable to fetch page {page} "
        f"after {MAX_RETRIES} attempts."
    )


# --------------------------------------------------
# INGEST ALL PAGES
# --------------------------------------------------

def ingest_orders():

    all_orders = []

    with requests.Session() as session:

        # Fetch first page to discover total pages
        first_page = fetch_page(1, session)

        total_pages = first_page["total_pages"]

        all_orders.extend(first_page["data"])

        logger.info(
            f"Total pages to process: {total_pages}"
        )

        # Fetch remaining pages
        for page in range(2, total_pages + 1):

            result = fetch_page(page, session)

            all_orders.extend(result["data"])

    return all_orders


# --------------------------------------------------
# VALIDATE INGESTED DATA
# --------------------------------------------------

def validate_orders(orders):

    total_records = len(orders)

    unique_ids = {
        order["order_id"]
        for order in orders
    }

    unique_records = len(unique_ids)

    logger.info("DATA VALIDATION")
    logger.info("-------------------------")
    logger.info(f"Total records: {total_records}")
    logger.info(f"Unique order IDs: {unique_records}")

    if total_records != unique_records:

        raise ValueError(
            "Duplicate order IDs detected!"
        )

    logger.info("Data validation successful.")

    return True


# --------------------------------------------------
# MAIN PIPELINE
# --------------------------------------------------

def main():

    try:

        logger.info("STARTING API INGESTION PIPELINE")

        # Step 1: Extract
        orders = ingest_orders()

        # Step 2: Validate
        validate_orders(orders)

        # Step 3: Load
        inserted = load_orders(orders)

        # Step 4: Summary
        print("\n========== PIPELINE SUMMARY ==========")

        print(f"Fetched records: {len(orders)}")

        print(
            f"Unique records: "
            f"{len(set(o['order_id'] for o in orders))}"
        )

        print(f"Inserted records: {inserted}")

        print("Pipeline status: SUCCESS")

        print("======================================")

    except Exception:

        logger.exception(
            "API INGESTION PIPELINE FAILED"
        )

        raise


if __name__ == "__main__":
    main()
    