from fastapi import FastAPI, HTTPException, Request

app = FastAPI(title="Client IP Service")


@app.get("/")
async def get_client_ip(request: Request) -> dict[str, str]:
    """Return the network peer address reported by the ASGI server."""
    if request.client is None:
        raise HTTPException(status_code=500, detail="Client address is unavailable")

    return {"ip": request.client.host}


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "healthy"}


@app.get("/ready")
async def ready() -> dict[str, str]:
    return {"status": "ready"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000, proxy_headers=False)
