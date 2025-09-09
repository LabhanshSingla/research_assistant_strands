# web.py
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates

from search_and_summarize import orchestrator  # uses your existing MODEL + tools

app = FastAPI(title="AI Research Assistant")

# static files (optional; create ./static/style.css if you want)
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

# dev CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
)

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/api/query")
async def api_query(
    prompt: str = Form(...),
    max_results: int = Form(3),
    bullets: int = Form(5),
):
    """
    Calls your orchestrator agent. Internally it will:
      1) call arxiv_search (returns OBJECT dict),
      2) pass that OBJECT to summarize_papers (returns OBJECT dict),
      3) return a human-readable final answer string.
    """
    try:
        ask = (
            f"Find {max_results} papers on '{prompt}'. "
            f"Summarize each in {bullets} bullets. "
            "Then render a neat human-readable summary."
        )
        reply = str(orchestrator(ask))
        return JSONResponse({"query": prompt, "answer": reply, "max_results": max_results, "bullets": bullets})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)
