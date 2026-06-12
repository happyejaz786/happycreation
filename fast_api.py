from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from ai_chat import router as assistant_router

app = FastAPI(
    title="Happy Assistant Pro"
)

# ------------------------------------
# Static + Templates
# ------------------------------------

app.mount(
    "/static",
    StaticFiles(directory="static"),
    name="static"
)

templates = Jinja2Templates(
    directory="templates"
)

# ------------------------------------
# Pages
# ------------------------------------

@app.get("/", response_class=HTMLResponse)
async def dashboard(
    request: Request
):
    return templates.TemplateResponse(
        request=request,
        name="dashboard.html"
    )


@app.get("/assistant", response_class=HTMLResponse)
async def assistant(
    request: Request
):
    return templates.TemplateResponse(
        request=request,
        name="ai_chat.html"
    )

# ------------------------------------
# API
# ------------------------------------

app.include_router(
    assistant_router,
    prefix="/api",
    tags=["Happy Assistant"]
)

# ------------------------------------
# Health Check
# ------------------------------------

@app.get("/health")
async def health():

    return {
        "status": "online",
        "service": "Happy Assistant Pro"
    }

# ------------------------------------
# 404
# ------------------------------------

@app.exception_handler(404)
async def not_found(
    request: Request,
    exc
):
    return JSONResponse(
        status_code=404,
        content={
            "status": "error",
            "message": "Endpoint not found"
        }
    )