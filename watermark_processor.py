import logging
from datetime import datetime, timedelta, timezone

from database import get_connection

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger(__name__)

ALLOWED_LATENESS = timedelta(minutes=5)

EVENTS = [
    {
        "event_id": "EVT-001",
        "order_id": 101,
        "event_time": "2026-11-24T10:00:00+00:00",
        "amount": 500
    },
    {
        "event_id": "EVT-002",
        "order_id": 102,
        "event_time": "2026-11-24T10:05:00+00:00",
        "amount": 750
    },
    {
        "event_id": "EVT-003",
        "order_id": 103,
        "event_time": "2026-11-24T10:15:00+00:00",
        "amount": 900
    },
    {
        "event_id": "EVT-004",
        "order_id": 104,
        "event_time": "2026-11-24T10:08:00+00:00",
        "amount": 650
    }
]

def process_events(events):
    max_event_time = None

    connection = get_connection()

    try:
        with connection.cursor() as cursor:

            for event in events:
                event_time = datetime.fromisoformat(
                    event["event_time"]
                )

                received_at = datetime.now(timezone.utc)

                if (
                    max_event_time is None
                    or event_time > max_event_time
                ):
                    max_event_time = event_time

                watermark = max_event_time - ALLOWED_LATENESS

                logger.info(
                    "Processing %s | Event time: %s | Watermark: %s",
                    event["event_id"],
                    event_time,
                    watermark
                )

                common_values = (
                    event["event_id"],
                    event["order_id"],
                    event_time,
                    received_at,
                    event["amount"]
                )

                if event_time < watermark:
                    logger.warning(
                        "LATE EVENT DETECTED: %s",
                        event["event_id"]
                    )

                    cursor.execute(
                        """
                        INSERT INTO late_order_events
                        (
                            event_id,
                            order_id,
                            event_time,
                            received_at,
                            amount,
                            watermark_at_arrival,
                            late_reason
                        )
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (event_id) DO NOTHING
                        """,
                        common_values + (
                            watermark,
                            "Event time is behind the watermark"
                        )
                    )

                else:
                    logger.info(
                        "ON-TIME EVENT: %s",
                        event["event_id"]
                    )

                    cursor.execute(
                        """
                        INSERT INTO order_events
                        (
                            event_id,
                            order_id,
                            event_time,
                            received_at,
                            amount
                        )
                        VALUES (%s, %s, %s, %s, %s)
                        ON CONFLICT (event_id) DO NOTHING
                        """,
                        common_values
                    )

        connection.commit()
        logger.info("WATERMARK PROCESSING COMPLETED")

    except Exception:
        connection.rollback()
        logger.exception("Watermark processing failed")
        raise

    finally:
        connection.close()

if __name__ == "__main__":
    process_events(EVENTS)
    