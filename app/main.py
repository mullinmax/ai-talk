from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import markdown
import re
import os
from typing import Dict, Set, Tuple

app = FastAPI()

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

##########################################################
#   1) Parse the Markdown into a Jeopardy-like structure
##########################################################

# Each topic dict has: {
#   "category": "AI Basics",
#   "points": 200,
#   "title": "Machine Learning Intro",
#   "slides": [
#       { "slide_title": "Definition", "slide_html": "<p>...</p>" },
#       { "slide_title": "Types", "slide_html": "<ul>...</ul>" }
#   ]
# }
presentation_data = []            # All topics
categories_order = []             # Keep track of category order
category_points_map = {}          # { "AI Basics": set([200,400]) , ... }
lookup_map = {}                   # (cat, points) -> index in presentation_data

def parse_presentation():
    md_path = os.path.join(os.path.dirname(__file__), "presentation.md")
    if not os.path.exists(md_path):
        print("presentation.md not found!")
        return

    with open(md_path, "r", encoding="utf-8") as f:
        raw_md = f.read()

    # Split by lines matching "# Category: "
    category_blocks = re.split(r"(?m)^# Category:\s*", raw_md)
    for block in category_blocks:
        block = block.strip()
        if not block:
            continue
        lines = block.splitlines()
        category_name = lines[0].strip()  # e.g. "AI Basics"
        if category_name not in categories_order:
            categories_order.append(category_name)

        remainder = "\n".join(lines[1:])
        # Now parse each "## X: Title"
        section_blocks = re.split(r"(?m)^##\s*", remainder)
        for sb in section_blocks:
            sb = sb.strip()
            if not sb:
                continue
            sublines = sb.splitlines()
            header = sublines[0].strip()  # e.g. "200: Machine Learning Intro"
            match = re.match(r"(\d+)\s*:\s*(.*)", header)
            if match:
                points_str, topic_title = match.groups()
                points = int(points_str.strip())
                body_md = "\n".join(sublines[1:])
                # Parse "### Slide: Slide Title" inside
                slides_list = parse_sub_slides(body_md)

                presentation_data.append({
                    "category": category_name,
                    "points": points,
                    "title": topic_title.strip(),
                    "slides": slides_list
                })
                # Track categories + points
                if category_name not in category_points_map:
                    category_points_map[category_name] = set()
                category_points_map[category_name].add(points)

def parse_sub_slides(topic_md: str):
    """
    Looks for lines like "### Slide: Something"
    Returns a list of {slide_title, slide_html}
    If no sub-slides found, treat entire block as one slide.
    """
    # Split on "### Slide:"
    parts = re.split(r"(?m)^###\s*Slide:\s*", topic_md)
    slides = []
    if len(parts) > 1:
        # first part might be empty or leftover text
        # each subsequent part starts with a line "Title\nrestOfMd"
        # we'll parse them
        for i, block in enumerate(parts):
            if i == 0:
                # leftover text before the first ### Slide
                # if there's any content, treat it as a "generic" slide
                leftover = block.strip()
                if leftover:
                    # let's call it "Overview"
                    slides.append({
                        "slide_title": "Overview",
                        "slide_html": markdown.markdown(leftover, extensions=["fenced_code", "tables"])
                    })
                continue
            lines = block.splitlines()
            stitle = lines[0].strip()  # e.g. "Welcome"
            sbody = "\n".join(lines[1:])
            shtml = markdown.markdown(sbody, extensions=["fenced_code", "tables"])
            slides.append({
                "slide_title": stitle,
                "slide_html": shtml
            })
    else:
        # No sub-slide headings. The entire block is one slide
        shtml = markdown.markdown(topic_md, extensions=["fenced_code", "tables"])
        slides.append({
            "slide_title": "Slide",
            "slide_html": shtml
        })
    return slides

parse_presentation()

# Sort topics by (category_order, points)
presentation_data.sort(key=lambda x: (categories_order.index(x["category"]), x["points"]))

# Build a lookup map
for i, item in enumerate(presentation_data):
    cat = item["category"]
    pts = item["points"]
    lookup_map[(cat, pts)] = i

# =====================================
#   2) Vote toggles (IP-based, naive)
# =====================================
votes: Dict[Tuple[str, int], Set[str]] = {}

def get_client_ip(request: Request) -> str:
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host

# ======================================
#   3) Current display: topic + slide
# ======================================
# We'll start on a "cover" if it exists. (cat="Cover", points=0)
# Otherwise, -1 means "no selection."
default_cover_index = next((i for i, t in enumerate(presentation_data)
                            if t["category"] == "Cover" and t["points"] == 0), -1)
current_index = default_cover_index if default_cover_index != -1 else -1
slide_position = 0  # which slide within that topic

#################################
#       Audience View
#################################
@app.get("/audience_view", response_class=HTMLResponse)
async def get_audience_view(request: Request):
    """
    Display the Jeopardy table with clickable vote buttons.
    """
    return templates.TemplateResponse("audience_view.html", {
        "request": request,
        "categories_order": categories_order,
        "category_points_map": category_points_map
    })

@app.get("/api/vote_data")
async def api_vote_data():
    """
    Return a structure with categories & points & vote counts
    e.g. { "AI Basics": {200: <count>, 400: <count>}, ... }
    """
    data = {}
    for cat in categories_order:
        data[cat] = {}
        if cat in category_points_map:
            for pts in sorted(category_points_map[cat]):
                key = (cat, pts)
                data[cat][pts] = len(votes.get(key, set()))
    return data

@app.post("/api/toggle_vote")
async def toggle_vote(request: Request, category: str = Form(...), points: int = Form(...)):
    ip = get_client_ip(request)
    key = (category, points)
    if key not in votes:
        votes[key] = set()
    if ip in votes[key]:
        votes[key].remove(ip)  # un-vote
    else:
        votes[key].add(ip)     # vote
    return {"status": "ok", "voteCount": len(votes[key])}

#################################
#       Presenter View
#################################
@app.get("/presenter_view", response_class=HTMLResponse)
async def get_presenter_view(request: Request):
    """
    Shows the same table with vote counts, plus a way to select a topic
    and also next/previous slide buttons.
    """
    return templates.TemplateResponse("presenter_view.html", {
        "request": request,
        "categories_order": categories_order,
        "category_points_map": category_points_map
    })

@app.post("/api/select_topic")
async def select_topic(category: str = Form(...), points: int = Form(...)):
    """
    Presenter clicks a topic. We jump the screen to that topic, slide 0.
    """
    global current_index, slide_position
    idx = lookup_map.get((category, points), -1)
    if idx != -1:
        current_index = idx
        slide_position = 0
    return {"status": "ok", "selected_index": current_index, "slide_position": slide_position}

@app.post("/api/nav_slide")
async def nav_slide(action: str = Form(...)):
    """
    next/prev within the currently selected topic.
    Or if you wanted global next/prev across topics, you'd do it differently.
    """
    global current_index, slide_position
    if current_index < 0 or current_index >= len(presentation_data):
        return {"current_index": current_index, "slide_position": slide_position}

    topic = presentation_data[current_index]
    slides = topic["slides"]
    if action == "next":
        if slide_position < len(slides) - 1:
            slide_position += 1
    elif action == "prev":
        if slide_position > 0:
            slide_position -= 1

    return {"current_index": current_index, "slide_position": slide_position}

#################################
#         Screen View
#################################
@app.get("/screen_view", response_class=HTMLResponse)
async def get_screen_view(request: Request):
    return templates.TemplateResponse("screen_view.html", {"request": request})

@app.get("/api/current_slide")
async def api_current_slide():
    """
    Return the currently selected topic & slide.
    If none selected, show the cover or "No Selection".
    """
    global current_index, slide_position
    if current_index < 0 or current_index >= len(presentation_data):
        return {
            "title": "No Selection",
            "content": "",
            "slide": 0,
            "slide_count": 0
        }
    topic = presentation_data[current_index]
    slides = topic["slides"]
    if slide_position < 0 or slide_position >= len(slides):
        # out of range
        return {
            "title": topic["title"],
            "content": "",
            "slide": 0,
            "slide_count": len(slides)
        }
    current_slide = slides[slide_position]
    return {
        "category": topic["category"],
        "points": topic["points"],
        "topicTitle": topic["title"],
        "slideTitle": current_slide["slide_title"],
        "content": current_slide["slide_html"],
        "slide": slide_position,
        "slide_count": len(slides)
    }

@app.get("/")
async def root():
    return RedirectResponse("/audience_view")
