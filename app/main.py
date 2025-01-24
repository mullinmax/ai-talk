from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI()

# Mount static directory for JS/CSS assets
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Jinja2 templates
templates = Jinja2Templates(directory="app/templates")

# In-memory data store for topics and votes
# For a real app, you'd likely use a database
topics = {
    "Topic 1": 0,
    "Topic 2": 0,
    "Topic 3": 0,
    "Topic 4": 0,
    "Topic 5": 0
}

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """
    Could be a welcome or redirect. Let's just redirect to the audience view.
    """
    return RedirectResponse(url="/audience_view")

@app.get("/audience_view", response_class=HTMLResponse)
async def get_audience_view(request: Request):
    """
    View for audience to cast their votes via simple buttons.
    """
    return templates.TemplateResponse("audience_view.html", {"request": request, "topics": topics})

@app.get("/presenter_view", response_class=HTMLResponse)
async def get_presenter_view(request: Request):
    """
    View for presenter to see real-time tallies and select the next topic.
    """
    # Sort topics by descending number of votes
    sorted_topics = sorted(topics.items(), key=lambda x: x[1], reverse=True)
    return templates.TemplateResponse("presenter_view.html", {"request": request, "sorted_topics": sorted_topics})

@app.get("/screen_view", response_class=HTMLResponse)
async def get_screen_view(request: Request):
    """
    Screen view that displays the slides/selected topic.
    We'll keep it simple for now; can be expanded to show actual slides.
    """
    return templates.TemplateResponse("screen_view.html", {"request": request})

@app.post("/vote", response_class=HTMLResponse)
async def post_vote(topic: str = Form(...)):
    """
    Endpoint to handle voting for a given topic.
    A simple POST with form data "topic".
    """
    if topic in topics:
        topics[topic] += 1
    return RedirectResponse(url="/audience_view", status_code=303)

@app.post("/select_topic", response_class=HTMLResponse)
async def select_topic(topic: str = Form(...)):
    """
    Presenter picks a topic to move slides forward.
    We can store 'selected_topic' in memory or do something else with it.
    For now, let's just redirect to the screen view (or back to presenter view).
    """
    # You might store this in a global or DB to show on screen
    # For example, set selected_topic in a global variable or an external state manager.
    # selected_topic = topic

    # For now, just redirect to screen_view.
    return RedirectResponse(url="/screen_view", status_code=303)
