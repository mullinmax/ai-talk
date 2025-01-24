// presenter.js

async function fetchVoteData() {
    try {
      let res = await fetch('/api/vote_data');
      let data = await res.json();
      renderPresenterTable(data);
    } catch (err) {
      console.error("fetchVoteData error:", err);
    }
  }
  
  function renderPresenterTable(voteData) {
    const tbody = document.getElementById('presenter-table-body');
    tbody.innerHTML = '';
  
    let cats = Object.keys(voteData).filter(cat => cat !== "Cover");
    // Gather all points
    let allPoints = new Set();
    cats.forEach(cat => {
      Object.keys(voteData[cat]).forEach(p => allPoints.add(parseInt(p)));
    });
    let sortedPoints = Array.from(allPoints).sort((a,b) => a - b);
  
    sortedPoints.forEach(ptVal => {
      let tr = document.createElement('tr');
      let tdPoints = document.createElement('td');
      tdPoints.textContent = ptVal;
      tr.appendChild(tdPoints);
  
      cats.forEach(cat => {
        let td = document.createElement('td');
        td.classList.add('p-2');
  
        let count = voteData[cat][ptVal] || 0;
        // We'll have a "Select" button
        let btn = document.createElement('button');
        btn.className = "btn btn-warning";
        btn.textContent = `${count} votes (Select)`;
        btn.onclick = () => selectTopic(cat, ptVal);
  
        td.appendChild(btn);
        tr.appendChild(td);
      });
      tbody.appendChild(tr);
    });
  }
  
  async function selectTopic(category, points) {
    let formData = new FormData();
    formData.append('category', category);
    formData.append('points', points);
    try {
      let res = await fetch('/api/select_topic', {
        method: 'POST',
        body: formData
      });
      let json = await res.json();
      console.log("selectTopic result:", json);
    } catch (err) {
      console.error("selectTopic error:", err);
    }
  }
  
  async function navSlide(action) {
    let formData = new FormData();
    formData.append('action', action);
    try {
      let res = await fetch('/api/nav_slide', { method: 'POST', body: formData });
      let json = await res.json();
      console.log("navSlide result:", json);
    } catch (err) {
      console.error("navSlide error:", err);
    }
  }
  
  setInterval(fetchVoteData, 1000);
  fetchVoteData();
  