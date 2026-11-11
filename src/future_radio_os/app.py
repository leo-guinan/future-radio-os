from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from future_radio_os import __version__
from future_radio_os.studio import StudioReadModel

SERVICE_NAME = "future-radio-os"


def create_app(studio: StudioReadModel | None = None) -> FastAPI:
    app = FastAPI(title="Future Radio OS", version=__version__)
    studio_model = studio or StudioReadModel()

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

    @app.get("/studio")
    def studio_read() -> dict[str, list[dict[str, str]]]:
        return studio_model.snapshot()

    @app.get("/studio/view", response_class=HTMLResponse)
    def studio_view() -> str:
        return studio_model.render_html()

    return app


app = create_app()