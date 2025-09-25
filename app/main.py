from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers import ideas, assess


def create_app() -> FastAPI:
    app = FastAPI(title="AI Venture Assessor", version="0.1.0")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/health")
    def health():
        return {"status": "ok"}

    app.include_router(ideas.router, prefix="/api/v1", tags=["ideas"]) 
    app.include_router(assess.router, prefix="/api/v1", tags=["assess"]) 

    return app


app = create_app()

