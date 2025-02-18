from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from typing import Dict, Set, Tuple
import uuid

app = FastAPI()
templates = Jinja2Templates(directory="app/templates")  # or wherever you moved your templates

# ------------------
# DATA STRUCTURES
# ------------------

user_votes: Dict[str, Set[Tuple[str, str]]] = {}  # user_id => set of (topic, subtopic_title)
vote_counts: Dict[Tuple[str, str], int] = {}       # (topic, subtopic_title) => vote count
disabled: Set[Tuple[str, str]] = set()             # set of (topic, subtopic_title) that are disabled

# Each subtopic is a dict with "title" and "link"
topics = {
    "History": [
        {"title": "1950's to 2019", "link": "https://example.com/history-1950-2019"},
        {"title": "The rise of LLMs", "link": "https://example.com/history-llms"},
        {"title": "not-so-openAI", "link": "https://example.com/not-so-openai"},
        {"title": "Reasoning Models", "link": "https://example.com/reasoning-models"},
    ],
    "How AI works": [
        {"title": "Neural Networks", "link": "https://example.com/neural-networks"},
        {"title": "Overview of LLMs", "link": "https://example.com/overview-llms"},
        {"title": "Tokenization & Embeddings", "link": "https://example.com/token-embed"},
    ],
    "Impact": [
        {"title": "Copyright law", "link": "https://example.com/copyright"},
        {"title": "Super Intelligence", "link": "https://example.com/super-intelligence"},
        {"title": "Environmental", "link": "https://example.com/environmental"},
        {"title": "Biomedical", "link": "https://example.com/biomedical"},
        {"title": "Misinformation", "link": "https://example.com/misinformation"},
    ],
    "Demos": [
        {"title": "Conversational models", "link": "https://example.com/conversational"},
        {"title": "Programming", "link": "https://example.com/programming"},
        {"title": "Music and Audio", "link": "https://example.com/music-audio"},
        {"title": "Image & Video", "link": "https://example.com/image-video"},
        {"title": "Autonomous vehicles", "link": "https://example.com/autonomous"},
    ],
}

# Initialize vote_counts
for topic, sub_list in topics.items():
    for sub in sub_list:
        pair = (topic, sub["title"])
        vote_counts[pair] = 0

# ------------------
# HELPER FUNCTIONS
# ------------------

def calculate_percentages() -> Dict[Tuple[str, str], float]:
    total = sum(v for v in vote_counts.values() if v > 0)
    if total == 0:
        return {k: 0.0 for k in vote_counts}
    
    result = {}
    for pair, count in vote_counts.items():
        if count > 0:
            result[pair] = (count / total) * 100
        else:
            result[pair] = 0.0
    return result

def toggle_vote(user_id: str, topic: str, subtopic_title: str):
    pair = (topic, subtopic_title)
    if user_id not in user_votes:
        user_votes[user_id] = set()
    
    if pair in user_votes[user_id]:
        # user un-votes
        user_votes[user_id].remove(pair)
        vote_counts[pair] -= 1
    else:
        # user votes
        user_votes[user_id].add(pair)
        vote_counts[pair] += 1

# ------------------
# AUDIENCE ROUTES
# ------------------

@app.get("/", response_class=HTMLResponse)
async def audience_page(request: Request):
    return templates.TemplateResponse("audience.html", {
        "request": request,
        "topics": topics
    })

@app.post("/vote", response_class=JSONResponse)
async def vote(user_id: str = Form(...), topic: str = Form(...), subtopic: str = Form(...)):
    pair = (topic, subtopic)
    if pair in disabled:
        return {"status": "disabled"}
    
    toggle_vote(user_id, topic, subtopic)
    return {"status": "ok"}

@app.get("/audience/data/{user_id}", response_class=JSONResponse)
async def get_audience_data(user_id: str):
    voted = list(user_votes.get(user_id, set()))
    disabled_list = list(disabled)
    return {"voted": voted, "disabled": disabled_list}

# ------------------
# PRESENTER ROUTES
# ------------------

@app.get("/presenter", response_class=HTMLResponse)
async def presenter_page(request: Request):
    return templates.TemplateResponse("presenter.html", {
        "request": request,
        "topics": topics
    })

@app.get("/presenter/data", response_class=JSONResponse)
async def presenter_data():
    """
    Return the current subtopic data to the presenter, including:
      - The subtopic's display title
      - The subtopic's vote percentage
      - Whether it is disabled
      - The link for the subtopic
    """
    percentages = calculate_percentages()
    data = []
    for topic, sub_list in topics.items():
        for sub in sub_list:
            pair = (topic, sub["title"])
            data.append({
                "topic": topic,
                "subtopic_title": sub["title"],
                "percentage": round(percentages[pair], 2),
                "disabled": pair in disabled,
                "link": sub["link"]
            })
    return {"data": data}

@app.post("/presenter/disable", response_class=JSONResponse)
async def presenter_disable(topic: str = Form(...), subtopic: str = Form(...)):
    pair = (topic, subtopic)
    disabled.add(pair)
    return {"status": "ok"}

@app.post("/reset", response_class=JSONResponse)
async def reset_votes():
    user_votes.clear()
    disabled.clear()
    for k in vote_counts:
        vote_counts[k] = 0
    return {"status": "ok", "message": "All votes have been reset."}
