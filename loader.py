
import logging
from database import get_connection

logger = logging.getLogger(__name__)


def load_orders(orders):
    if not orders:
        logger.warning("No orders received for loading.")
        return 0

    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            query = """
                INSERT INTO api_orders
                    (order_id, customer_name, amount)
                VALUES (%s, %s, %s)
                ON CONFLICT (order_id) DO NOTHING;
            """

            values = [
                (
                    order["order_id"],
                    order["customer"],
                    order["amount"]
                )
                for order in orders
            ]

            cursor.executemany(query, values)

            inserted_count = cursor.rowcount

        connection.commit()

        logger.info(
            "Successfully inserted %s orders",
            inserted_count
        )

        return inserted_count

    except Exception:
        connection.rollback()
        logger.exception("Database loading failed")
        raise

    finally:
        connection.close()
