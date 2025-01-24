# AI Talk - Jeopardy-Style Presentation

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Docker Publish](https://github.com/YourUsername/YourRepo/actions/workflows/docker-publish.yml/badge.svg)](https://github.com/YourUsername/YourRepo/actions)

This project is a **FastAPI** web app for running a Jeopardy-style, audience-interactive presentation.  
It was designed as a **one-off** for a senior center AI talk, but feel free to **fork** and adapt it to your needs!

## Features

- **Audience View**: Shows a grid of topics (categories & point values). Audience members can tap to **vote/unvote** on a topic.  
- **Presenter View**: Shows real-time votes and allows the presenter to **select** a topic. Also offers **Next/Previous** slide controls for deeper topics.  
- **Screen View**: Displays the currently selected topic/slide in real time.

## How It Works

1. **Markdown-based** presentation. You define categories, topics (with “## Points: Title”), and **slides** (with “### Slide: …”).  
2. The app **parses** the Markdown into an internal structure.  
3. **Votes** are tracked per (category, points) pair.  
4. The **presenter** can override audience votes by selecting any topic.  
5. Each topic can have **multiple slides**, navigable by next/previous on the presenter side.  
6. The **screen** automatically shows whichever slide is selected.

## Setup Instructions

1. **Clone or Fork** this repo:
```bash
git clone https://github.com/YourUsername/YourRepo.git
cd YourRepo
```
2. **Install Python dependencies**:
```bash
pip install -r requirements.txt
```
Or use a virtual environment:
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

3. **Run**:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```
Then open http://localhost:8000 in your browser.

## Docker

A Dockerfile is provided. You can build and run locally:
```bash
docker build -t ai-talk .
docker run -p 8000:80 ai-talk
```
Then visit http://localhost:8000.

If you have the GitHub Workflow set up, pushing to main will build & push an image to GitHub Container Registry (GHCR).

## Contributing

This is provided “as-is” under the MIT License.  
We do not plan to maintain it long-term. Fork away and customize to your heart’s content!

## License

MIT License [LICENSE](LICENSE)
```
