import os
import httpx

PRODUCT_API_BASE_URL = os.getenv("PRODUCT_API_BASE_URL", "https://qr-blockchain-api.vercel.app")


async def fetch_product_data(container_id: str) -> list[dict]:
    url = f"{PRODUCT_API_BASE_URL}/product-data"

    async with httpx.AsyncClient(timeout=15.0) as client:
        response = await client.get(url, params={"containerID": container_id})

    response.raise_for_status()
    return response.json()   # returns a list of dicts