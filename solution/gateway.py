import json
import logging

import httpx
from fastapi import FastAPI, HTTPException


logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger("gateway-service")
app = FastAPI(title="Gateway Service")


@app.get("/order")
async def create_order() -> dict[str, object]:
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.post(
                "http://payment-service:5001/charge",
                json={"amount": 42.00, "currency": "USD"},
            )
            response.raise_for_status()
    except httpx.HTTPStatusError as error:
        logger.error(
            json.dumps(
                {
                    "service": "gateway-service",
                    "event": "payment_error",
                    "status_code": error.response.status_code,
                    "detail": error.response.text,
                }
            )
        )
        raise HTTPException(status_code=502, detail="payment service failed") from error
    except httpx.HTTPError as error:
        logger.error(
            json.dumps(
                {
                    "service": "gateway-service",
                    "event": "payment_unavailable",
                    "detail": str(error),
                }
            )
        )
        raise HTTPException(status_code=502, detail="payment service unavailable") from error

    logger.info(
        json.dumps(
            {
                "service": "gateway-service",
                "event": "order_created",
                "payment": response.json(),
            }
        )
    )
    return {"order_id": "local-demo-order", "payment": response.json()}