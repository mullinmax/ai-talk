// audience.js

// We'll fetch the categories_order from the template, or just parse from the DOM if needed.
// For demonstration, let's do a dynamic approach: call /api/vote_data, reconstruct the table.

async function fetchVoteData() {
    try {
      let res = await fetch('/api/vote_data');
      let data = await res.json();
      // data = { "AI Basics": { 200: <count>, 400: <count> }, "Applications": { 200: <count>, ... } }
      renderTable(data);
    } catch (err) {
      console.error("Error fetching vote data:", err);
    }
  }
  
  function renderTable(voteData) {
    const tbody = document.getElementById('audience-table-body');
    tbody.innerHTML = '';
  
    // We only want categories except "Cover"
    let cats = Object.keys(voteData).filter(cat => cat !== "Cover");
    // Gather all point values
    let allPoints = new Set();
    cats.forEach(cat => {
      Object.keys(voteData[cat]).forEach(p => allPoints.add(parseInt(p)));
    });
    let sortedPoints = Array.from(allPoints).sort((a,b) => a - b);
  
    // Build rows by points
    sortedPoints.forEach(ptVal => {
      let tr = document.createElement('tr');
      // First cell: the point value
      let tdPoints = document.createElement('td');
      tdPoints.textContent = ptVal;
      tr.appendChild(tdPoints);
  
      // Each category is a column
      cats.forEach(cat => {
        let td = document.createElement('td');
        td.classList.add('p-2');
        let count = voteData[cat][ptVal] || 0;
  
        // Create a button
        let btn = document.createElement('button');
        btn.className = "btn btn-primary";
        btn.textContent = `${count} votes`;
        btn.onclick = () => toggleVote(cat, ptVal);
        td.appendChild(btn);
  
        tr.appendChild(td);
      });
      tbody.appendChild(tr);
    });
  }
  
  async function toggleVote(category, points) {
    let formData = new FormData();
    formData.append('category', category);
    formData.append('points', points);
  
    try {
      let res = await fetch('/api/toggle_vote', {
        method: 'POST',
        body: formData
      });
      let json = await res.json();
      console.log("toggleVote result:", json);
      fetchVoteData();
    } catch (err) {
      console.error("toggleVote error:", err);
    }
  }
  
  // Poll every 1 second
  setInterval(fetchVoteData, 1000);
  fetchVoteData();
  