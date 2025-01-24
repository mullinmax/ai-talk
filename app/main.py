from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import markdown
import re
import os

app = FastAPI()

# Mount static directory for JS/CSS
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Jinja2 templates
templates = Jinja2Templates(directory="app/templates")

# In-memory data store for topics and votes
topics = {
    "Topic 1": 0,
    "Topic 2": 0,
    "Topic 3": 0,
    "Topic 4": 0,
    "Topic 5": 0
}

# =========================
# 1) Parse Markdown slides
# =========================

# We'll parse the markdown file "presentation.md" and store slides in a list.
# Example approach: Split on '##' to find each slide after a category heading '#'
# This is just one simplistic approach. You might refine the regex or parsing logic.
slides = []  # Will store slide dicts: { "category": "Intro", "title": "Slide 1", "content": "...HTML..." }

def parse_presentation_file():
    md_path = os.path.join(os.path.dirname(__file__), "presentation.md")
    if not os.path.exists(md_path):
        return

    with open(md_path, "r", encoding="utf-8") as f:
        raw_markdown = f.read()

    # One naive approach: first split by single '# ' lines for categories,
    # then split by '## ' lines for slides. We'll store them all.
    # For maximum flexibility, you might do a full markdown AST parse. This is just a skeleton.
    category_blocks = re.split(r"(?m)^# ", raw_markdown)
    # The first chunk might be empty if file starts with "#".
    for block in category_blocks:
        block = block.strip()
        if not block:
            continue
        # The first line in this block is the category
        lines = block.splitlines()
        category_title = lines[0].replace("Category: ", "").strip()
        remainder = "\n".join(lines[1:])

        # Now split remainder by "## " for each slide
        slide_blocks = re.split(r"(?m)^## ", remainder)
        for s_block in slide_blocks:
            s_block = s_block.strip()
            if not s_block:
                continue
            s_lines = s_block.splitlines()
            slide_title = s_lines[0].strip()
            slide_content_md = "\n".join(s_lines[1:])
            # Convert MD to HTML for display
            slide_content_html = markdown.markdown(slide_content_md, extensions=["fenced_code", "tables"])
            slides.append({
                "category": category_title,
                "title": slide_title,
                "content": slide_content_html
            })

# Parse the file on startup
parse_presentation_file()

# Keep a global pointer to the current slide index
current_slide_index = 0 if slides else -1  # -1 if no slides available

# ====================
# Audience (was senior_view)
# ====================
@app.get("/audience_view", response_class=HTMLResponse)
async def get_audience_view(request: Request):
    """
    View for audience to cast votes.
    """
    return templates.TemplateResponse("audience_view.html", {"request": request, "topics": topics})

@app.post("/vote", response_class=HTMLResponse)
async def post_vote(topic: str = Form(...)):
    """
    Handle voting for a given topic.
    """
    if topic in topics:
        topics[topic] += 1
    return RedirectResponse(url="/audience_view", status_code=303)

# ====================
# Presenter View
# ====================
@app.get("/presenter_view", response_class=HTMLResponse)
async def get_presenter_view(request: Request):
    """
    Presenter sees real-time tallies, can select slide navigation.
    """
    return templates.TemplateResponse("presenter_view.html", {"request": request})

@app.get("/api/votes")
async def api_votes():
    """
    Returns the sorted topics (by votes) as JSON for polling.
    """
    sorted_topics = sorted(topics.items(), key=lambda x: x[1], reverse=True)
    return {"topics": sorted_topics}

@app.post("/api/slide_control")
async def slide_control(action: str = Form(...)):
    """
    Actions: "next", "prev", "menu" (if you want to jump back to a main menu).
    We'll just set current_slide_index accordingly.
    """
    global current_slide_index
    if not slides:
        return JSONResponse({"message": "No slides loaded"}, status_code=400)

    if action == "next":
        if current_slide_index < len(slides) - 1:
            current_slide_index += 1
    elif action == "prev":
        if current_slide_index > 0:
            current_slide_index -= 1
    elif action == "menu":
        # Optional logic if you want to jump to a menu slide or do something else
        current_slide_index = 0  # or -1 to represent "no slide"

    return {"current_slide_index": current_slide_index}

# ====================
# Screen View
# ====================
@app.get("/screen_view", response_class=HTMLResponse)
async def get_screen_view(request: Request):
    """
    This view will show the current slide in real time (polled).
    """
    return templates.TemplateResponse("screen_view.html", {"request": request})

@app.get("/api/current_slide")
async def api_current_slide():
    """
    Returns the current slide (HTML) for screen_view to display.
    """
    if current_slide_index < 0 or current_slide_index >= len(slides):
        return {"title": "No slides", "content": ""}
    slide = slides[current_slide_index]
    return {
        "title": slide["title"],
        "category": slide["category"],
        "content": slide["content"],
        "index": current_slide_index,
        "total": len(slides)
    }

@app.get("/", response_class=HTMLResponse)
async def root():
    # Redirect to audience view or presenter view, your call.
    return RedirectResponse(url="/audience_view")
