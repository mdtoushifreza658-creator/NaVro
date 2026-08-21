"""
NaVro API — entrypoint.

M0: just a health check, so the first `uvicorn` run proves the skeleton
is wired correctly before any search logic exists.
"""

from fastapi import FastAPI

app = FastAPI(
    title="NaVro API",
    description="Embeddable search infrastructure — V1",
    version="0.0.1",
)


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "navro-api", "version": "0.0.1"}
