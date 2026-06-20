const API_URL = "";

// State
let activeGoals = JSON.parse(localStorage.getItem('ecoGoals')) || [];

// DOM Elements
const form = document.getElementById('ecoForm');
const btn = document.getElementById('analyzeBtn');
const resultsContent = document.getElementById('resultsContent');
const resultsPlaceholder = document.querySelector('.results-placeholder');
const insightText = document.getElementById('insightText');
const typingIndicator = document.getElementById('typingIndicator');
const activeGoalsList = document.getElementById('activeGoalsList');
const goalCount = document.getElementById('goalCount');

// Initialize Goals on load
renderGoals();

form.addEventListener('submit', async (e) => {
  e.preventDefault();
  
  // Set Loading State
  btn.disabled = true;
  btn.textContent = 'Agent Thinking...';
  btn.setAttribute('aria-busy', 'true');
  
  // Prepare payload according to backend UserHabits schema
  const payload = {
    transport: {
      mode: document.getElementById('transportMode').value,
      distance_km_per_day: parseFloat(document.getElementById('transportDist').value)
    },
    electricity: {
      hours_ac: parseFloat(document.getElementById('hoursAC').value),
      hours_fan: 0.0,
      hours_lights: 0.0,
      hours_appliances: 0.0
    },
    food_preference: document.getElementById('foodPref').value,
    shopping_level: document.getElementById('shoppingLevel').value,
    waste: {
      recycles: document.getElementById('recycles').checked,
      composts: document.getElementById('composts').checked
    },
    water_liters_per_day: 150.0,
    home_type: "Apartment" // Defaulting as it's not in the UI
  };

  try {
    const res = await fetch(`${API_URL}/analyze`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    if (!res.ok) throw new Error('API Error');
    const data = await res.json();
    
    displayResults(data);
  } catch (error) {
    alert('Oops! The EcoDNA agent encountered an issue. Please try again.');
    console.error(error);
  } finally {
    btn.disabled = false;
    btn.textContent = 'Analyze Footprint';
    btn.setAttribute('aria-busy', 'false');
  }
});

function displayResults(data) {
  // Hide placeholder, show results
  resultsPlaceholder.classList.add('hidden');
  resultsContent.classList.remove('hidden');

  // Update Score & Co2
  document.getElementById('carbonScore').textContent = Math.round(data.footprint.carbon_score);
  document.getElementById('totalCo2').textContent = data.footprint.total_co2.toFixed(2);

  // Update Breakdown
  const breakdownList = document.getElementById('breakdownList');
  breakdownList.innerHTML = `
    <li><span>Transport</span> <span>${data.footprint.transport_co2.toFixed(2)} kg</span></li>
    <li><span>Electricity</span> <span>${data.footprint.electricity_co2.toFixed(2)} kg</span></li>
    <li><span>Food</span> <span>${data.footprint.food_co2.toFixed(2)} kg</span></li>
    <li><span>Shopping</span> <span>${data.footprint.shopping_co2.toFixed(2)} kg</span></li>
    <li><span>Waste</span> <span>${data.footprint.waste_co2.toFixed(2)} kg</span></li>
  `;

  // Update Interactive Recommendations
  const recsList = document.getElementById('recommendationsList');
  recsList.innerHTML = data.recommendations.map(r => `
    <li data-action="${r.action}" data-impact="${r.effort_level}">
      <strong>${r.category}</strong>
      ${r.action}
    </li>
  `).join('');

  // Add event listeners to recommendations
  document.querySelectorAll('.interactive-list li').forEach(item => {
    item.addEventListener('click', () => {
      addGoal(item.dataset.action);
    });
  });

  // Type out the Agent Insight
  typeAgentMessage(data.weekly_report);
}

function typeAgentMessage(text) {
  insightText.textContent = "";
  typingIndicator.classList.remove('hidden');
  
  // Simulate network thinking delay before typing
  setTimeout(() => {
    typingIndicator.classList.add('hidden');
    let i = 0;
    insightText.textContent = "";
    
    // Quick typing effect
    const interval = setInterval(() => {
      insightText.textContent += text.charAt(i);
      i++;
      if (i >= text.length) clearInterval(interval);
    }, 20);
  }, 1000);
}

function addGoal(actionText) {
  // Prevent duplicates
  if (activeGoals.find(g => g.title === actionText)) {
    alert('You are already tracking this goal!');
    return;
  }

  activeGoals.push({
    id: Date.now(),
    title: actionText,
    progress: Math.floor(Math.random() * 20) + 5 // Random initial progress 5-25%
  });

  saveGoals();
  renderGoals();
}

function saveGoals() {
  localStorage.setItem('ecoGoals', JSON.stringify(activeGoals));
}

function renderGoals() {
  goalCount.textContent = `${activeGoals.length} Active`;
  
  if (activeGoals.length === 0) {
    activeGoalsList.innerHTML = `<p class="empty-state">No goals tracked yet. Click a suggestion to start tracking!</p>`;
    return;
  }

  activeGoalsList.innerHTML = activeGoals.map(goal => `
    <div class="goal-card">
      <div class="goal-title">${goal.title}</div>
      <div style="display:flex; justify-content:space-between; font-size:0.8rem; color:var(--text-secondary)">
        <span>Progress</span>
        <span>${goal.progress}%</span>
      </div>
      <div class="goal-progress">
        <div class="goal-progress-bar" style="width: ${goal.progress}%"></div>
      </div>
    </div>
  `).join('');
}
