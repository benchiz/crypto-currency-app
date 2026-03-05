from fastapi import FastAPI, HTTPException, Query
import httpx
from datetime import datetime
import uvicorn
from contextlib import asynccontextmanager
import logging

from config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.http_client = httpx.AsyncClient(
        timeout=30.0,
        headers={"Accept": "application/json",
                 "User-Agent": "CryptoCurrencyApp/1.0"}
    )
    logger.info("Application started")
    yield

    await app.state.http_client.aclose()
    logger.info("Application stopped")


app = FastAPI(
    title="Cryptocurrency Service",
    description="Микросервис для получения курсов криптовалют",
    version=settings.VERSION,
    lifespan=lifespan
)


@app.get("/", tags=["Root"])
async def root():
    return {
        "message": "Cryptocurrency Service API",
        "docs": "/docs",
        "info": "/info",
        "cryptocurrency": "/info/cryptocurrency"
    }


@app.get("/info", tags=["Information"])
async def get_info():
    return {
        "version": settings.VERSION,
        "service": settings.SERVICE_NAME
    }


@app.get("/info/cryptocurrency", tags=["Cryptocurrency"])
async def get_cryptocurrency_prices(
    ids: str = Query("bitcoin,ethereum,tether",
                     description="Список криптовалют через запятую"),
    vs_currencies: str = Query(
        "usd,eur,rub", description="Список валют через запятую")
):
    logger.info(
        f"Request for cryptocurrencies: {ids}, currencies: {vs_currencies}")

    try:
        url = f"{settings.COINGECKO_API_URL}/simple/price"
        params = {
            "ids": ids,
            "vs_currencies": vs_currencies,
            "include_last_updated_at": True
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()

        if not data:
            raise HTTPException(
                status_code=404, detail=f"Криптовалюты не найдены: {ids}. Проверьте правильность написания.")

        # Форматируем ответ
        found_any = False
        result = []

        for crypto_id, prices in data.items():
            for currency, price in prices.items():
                if currency != "last_updated_at" and price is not None:
                    result.append({
                        "cryptocurrency": crypto_id,
                        "currency": currency.upper(),
                        "current_price": float(price) if price else 0,
                        "last_updated": datetime.fromtimestamp(
                            data[crypto_id].get(
                                "last_updated_at", datetime.now().timestamp())
                        ).isoformat()
                    })
                    found_any = True

        if not found_any:
            raise HTTPException(
                status_code=404,
                detail=f"Для указанных криптовалют не найдены цены: {ids}"
            )

        logger.info(f"Successfully retrieved {len(result)} price entries")
        return result

    except httpx.TimeoutException:
        logger.error("Timeout connecting to CoinGecko")
        raise HTTPException(
            status_code=504,
            detail="Сервис CoinGecko не отвечает"
        )
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error from CoinGecko: {e.response.status_code}")
        if e.response.status_code == 429:
            raise HTTPException(
                status_code=429,
                detail="Превышен лимит запросов к CoinGecko. Попробуйте позже"
            )
        elif e.response.status_code == 404:
            raise HTTPException(
                status_code=404,
                detail="Запрошенные криптовалюты не найдены"
            )
        else:
            raise HTTPException(
                status_code=502,
                detail=f"Ошибка сервиса CoinGecko: {e.response.status_code}"
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        raise HTTPException(
            status_code=500,
            detail="Внутренняя ошибка сервера"
        )


@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "healthy",
        "version": settings.VERSION,
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.PORT,
        reload=True
    )
