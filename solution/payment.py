import asyncio
import json
import logging
import os
import random
import time

from fastapi import FastAPI, HTTPException


logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger("payment-service")
app = FastAPI(title="Payment Service")
failure_rate = float(os.getenv("PAYMENT_FAIL_RATE", "0"))


@app.post("/charge")
async def charge() -> dict[str, object]:
    started_at = time.perf_counter()
    delay_ms = random.randint(100, 400)
    await asyncio.sleep(delay_ms / 1000)

    if random.random() < failure_rate:
        duration_ms = round((time.perf_counter() - started_at) * 1000, 2)
        logger.error(
            json.dumps(
                {
                    "service": "payment-service",
                    "event": "charge_failed",
                    "duration_ms": duration_ms,
                    "reason": "simulated outage",
                }
            )
        )
        raise HTTPException(status_code=500, detail="simulated payment outage")

    duration_ms = round((time.perf_counter() - started_at) * 1000, 2)
    logger.info(
        json.dumps(
            {
                "service": "payment-service",
                "event": "charge_succeeded",
                "duration_ms": duration_ms,
                "amount": 42.00,
                "currency": "USD",
            }
        )
    )
    return {"status": "charged", "amount": 42.00, "currency": "USD"}