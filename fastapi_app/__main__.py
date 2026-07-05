"""Entry point to start the API server: ``python -m fastapi_app``."""

import uvicorn

from fastapi_app.core.config import settings


def main() -> None:
    """Run the API server using settings from the environment."""
    uvicorn.run(
        "fastapi_app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.RELOAD,
    )


if __name__ == "__main__":
    main()
