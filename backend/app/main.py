from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from typing import Dict, Set, Tuple
import uuid

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# ------------------
# DATA STRUCTURES
# ------------------

# We'll store:
# - user_votes: which subtopics a specific user has chosen
# - vote_counts: how many total votes each (topic, subtopic) has
# - disabled: which (topic, subtopic) is disabled by the presenter
user_votes: Dict[str, Set[Tuple[str, str]]] = {}
vote_counts: Dict[Tuple[str, str], int] = {}
disabled: Set[Tuple[str, str]] = set()

# Topics and subtopics
topics = {
    "History": [
        "1950's to 2019",
        "The rise of LLMs",
        "not-so-openAI",
        "Reasoning Models",
    ],
    "How AI works": [
        "Neural Networks",
        "Overview of LLMs",
        "Tokenization & Embeddings",
    ],
    "Impact": [
        "Copyright law",
        "Super Intelligence",
        "Environmental",
        "Biomedical",
        "Misinformation",
    ],
    "Demos": [
        "Conversational models",
        "Programming",
        "Music and Audio",
        "Image & Video",
        "Autonomous vehicles",
    ],
}

# Initialize vote_counts with zero
for t in topics:
    for sub in topics[t]:
        vote_counts[(t, sub)] = 0

# ------------------
# HELPER FUNCTIONS
# ------------------

def calculate_percentages() -> Dict[Tuple[str, str], float]:
    """
    Calculate the percentage for each (topic, subtopic) based on total votes.
    """
    total = sum(v for k, v in vote_counts.items() if v > 0)
    if total == 0:
        # If no votes yet, each subtopic is 0%
        return {k: 0.0 for k in vote_counts}
    
    percentages = {}
    for k, v in vote_counts.items():
        if v > 0:
            percentages[k] = (v / total) * 100
        else:
            percentages[k] = 0.0
    return percentages

def toggle_vote(user_id: str, topic: str, subtopic: str):
    """
    Toggle the user's vote for (topic, subtopic).
    If user had voted, remove that vote. Otherwise, add it.
    """
    pair = (topic, subtopic)
    # If not present, initialize
    if user_id not in user_votes:
        user_votes[user_id] = set()
    
    if pair in user_votes[user_id]:
        # User removes their vote
        user_votes[user_id].remove(pair)
        vote_counts[pair] -= 1
    else:
        # User adds a vote
        user_votes[user_id].add(pair)
        vote_counts[pair] += 1

# ------------------
# AUDIENCE ROUTES
# ------------------

@app.get("/", response_class=HTMLResponse)
async def audience_page(request: Request):
    """
    Serve the audience voting page (templates/audience.html).
    """
    return templates.TemplateResponse("audience.html", {"request": request, "topics": topics})

@app.post("/vote", response_class=JSONResponse)
async def vote(user_id: str = Form(...), topic: str = Form(...), subtopic: str = Form(...)):
    """
    Toggle the user's vote for a given (topic, subtopic).
    Returns JSON with "ok" or "disabled".
    """
    pair = (topic, subtopic)
    # If a subtopic is disabled, do nothing
    if pair in disabled:
        return {"status": "disabled", "message": "Subtopic is disabled."}
    
    toggle_vote(user_id, topic, subtopic)
    return {"status": "ok"}

@app.get("/audience/data/{user_id}", response_class=JSONResponse)
async def get_audience_data(user_id: str):
    """
    Return which subtopics the user has voted for and
    which subtopics are disabled, so the UI can be updated.
    """
    voted_pairs = user_votes.get(user_id, set())
    # Convert set of tuples to list
    voted_list = list(voted_pairs)
    disabled_list = list(disabled)
    return {"voted": voted_list, "disabled": disabled_list}

# ------------------
# PRESENTER ROUTES
# ------------------

@app.get("/presenter", response_class=HTMLResponse)
async def presenter_page(request: Request):
    """
    Serve the presenter page (templates/presenter.html).
    """
    return templates.TemplateResponse("presenter.html", {"request": request, "topics": topics})

@app.get("/presenter/data", response_class=JSONResponse)
async def presenter_data():
    """
    Return JSON containing the current vote percentages
    and which subtopics are disabled.
    """
    percentages = calculate_percentages()
    data = []
    for t in topics:
        for sub in topics[t]:
            pair = (t, sub)
            data.append({
                "topic": t,
                "subtopic": sub,
                "percentage": round(percentages[pair], 2),
                "disabled": (pair in disabled),
            })
    return {"data": data}

@app.post("/presenter/disable", response_class=JSONResponse)
async def presenter_disable(topic: str = Form(...), subtopic: str = Form(...)):
    """
    Disable a subtopic so the audience can no longer vote on it.
    """
    pair = (topic, subtopic)
    disabled.add(pair)
    return {"status": "ok"}

@app.post("/reset", response_class=JSONResponse)
async def reset_votes():
    """
    Reset all votes (clears the entire poll).
    """
    user_votes.clear()
    disabled.clear()
    for k in vote_counts:
        vote_counts[k] = 0
    return {"status": "ok", "message": "All votes have been reset."}
