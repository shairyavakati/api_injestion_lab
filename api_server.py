
from fastapi import FastAPI, HTTPException, Query
import time

app = FastAPI(title="Mock E-commerce API")

# Simulate 1,000 orders
ORDERS = [
    {
        "order_id": i,
        "customer": f"Customer_{i}",
        "amount": round(100 + i * 2.5, 2)
    }
    for i in range(1, 1001)
]

# Track requests to simulate rate limiting
request_count = 0
rate_limit_triggered = False


@app.get("/orders")
def get_orders(page: int = Query(1, ge=1)):
    global request_count, rate_limit_triggered

    request_count += 1

    # Deliberately fail the third request once
    if request_count == 3 and not rate_limit_triggered:
        rate_limit_triggered = True
        raise HTTPException(
            status_code=429,
            detail="Too many requests. Please retry."
        )

    page_size = 100
    start = (page - 1) * page_size
    end = start + page_size

    return {
        "page": page,
        "page_size": page_size,
        "total_records": len(ORDERS),
        "total_pages": 10,
        "data": ORDERS[start:end]
    }
