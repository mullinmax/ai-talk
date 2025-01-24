// screen.js

async function fetchCurrentSlide() {
    try {
      let res = await fetch('/api/current_slide');
      let data = await res.json();
      // data = { title, content, slide, slide_count, category, points, topicTitle, ... }
      updateScreen(data);
    } catch (err) {
      console.error("fetchCurrentSlide error:", err);
    }
  }
  
  function updateScreen(data) {
    // If no selection
    const titleEl = document.getElementById('slide-title');
    const subtitleEl = document.getElementById('slide-subtitle');
    const contentEl = document.getElementById('slide-content');
    const footerEl = document.getElementById('slide-footer');
  
    if (!data || !data.content) {
      titleEl.textContent = data.title || "No Selection";
      subtitleEl.textContent = "";
      contentEl.innerHTML = "";
      footerEl.textContent = "";
      return;
    }
  
    titleEl.textContent = data.topicTitle || data.title;
    subtitleEl.textContent = data.slideTitle || "";
    contentEl.innerHTML = data.content || "";
    footerEl.textContent = `Slide ${data.slide + 1} of ${data.slide_count} ` +
                           (data.category ? ` | Category: ${data.category}, ${data.points} pts` : '');
  }
  
  // Poll every second for updates
  setInterval(fetchCurrentSlide, 1000);
  fetchCurrentSlide();
  