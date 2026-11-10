from fastapi import FastAPI

from future_radio_os import __version__

SERVICE_NAME = "future-radio-os"


def create_app() -> FastAPI:
    app = FastAPI(title="Future Radio OS", version=__version__)

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok", "service": SERVICE_NAME, "version": __version__}

    @app.get("/ready")
    def ready() -> dict[str, object]:
        return {
            "status": "ready",
            "service": SERVICE_NAME,
            "checks": {"configuration": "ok", "storage": "not_configured"},
        }

    return app


app = create_app()
