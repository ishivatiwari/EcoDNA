/**
 * @fileoverview EcoDNA Frontend Application
 *
 * Handles user interaction, API communication, result rendering,
 * and goal tracking for the EcoDNA sustainability assistant.
 * Uses safe DOM APIs exclusively (no innerHTML) to prevent XSS.
 *
 * @module main
 */

/** @type {string} Base URL for the backend API */
const API_URL = "";

/** @type {AbortController|null} Controller for in-flight fetch requests */
let activeController = null;

/** @type {Array<{id: number, title: string, progress: number}>} Active goals list */
let activeGoals = [];

try {
  const stored = localStorage.getItem("ecoGoals");
  if (stored) {
    activeGoals = JSON.parse(stored);
  }
} catch {
  activeGoals = [];
}

// ── DOM Element References ──────────────────
/** @type {HTMLFormElement} */
const form = document.getElementById("ecoForm");
/** @type {HTMLButtonElement} */
const btn = document.getElementById("analyzeBtn");
/** @type {HTMLElement} */
const resultsContent = document.getElementById("resultsContent");
/** @type {HTMLElement} */
const resultsPlaceholder = document.getElementById("resultsPlaceholder");
/** @type {HTMLElement} */
const insightText = document.getElementById("insightText");
/** @type {HTMLElement} */
const typingIndicator = document.getElementById("typingIndicator");
/** @type {HTMLElement} */
const activeGoalsList = document.getElementById("activeGoalsList");
/** @type {HTMLElement} */
const goalCount = document.getElementById("goalCount");

// ── Initialise ──────────────────────────────
renderGoals();

/**
 * Debounce guard — prevents rapid re-submissions.
 * @type {boolean}
 */
let isSubmitting = false;

form.addEventListener("submit", async (e) => {
  e.preventDefault();

  // Debounce guard
  if (isSubmitting) return;
  isSubmitting = true;

  // Cancel any in-flight request
  if (activeController) {
    activeController.abort();
  }
  activeController = new AbortController();

  // Set loading state
  btn.disabled = true;
  btn.textContent = "Agent Thinking...";
  btn.setAttribute("aria-busy", "true");

  // Build payload matching backend UserHabits schema
  const payload = {
    transport: {
      mode: document.getElementById("transportMode").value,
      distance_km_per_day: parseFloat(
        document.getElementById("transportDist").value
      ),
    },
    electricity: {
      hours_ac: parseFloat(document.getElementById("hoursAC").value),
      hours_fan: 0.0,
      hours_lights: 0.0,
      hours_appliances: 0.0,
    },
    food_preference: document.getElementById("foodPref").value,
    shopping_level: document.getElementById("shoppingLevel").value,
    waste: {
      recycles: document.getElementById("recycles").checked,
      composts: document.getElementById("composts").checked,
    },
    water_liters_per_day: parseFloat(
      document.getElementById("waterUsage").value
    ),
    home_type: document.getElementById("homeType").value,
  };

  try {
    const res = await fetch(`${API_URL}/analyze`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
      signal: activeController.signal,
    });

    if (!res.ok) {
      throw new Error(`API Error: ${res.status}`);
    }

    const data = await res.json();
    displayResults(data);
  } catch (error) {
    if (error.name === "AbortError") {
      // Request was cancelled — ignore
      return;
    }
    showErrorMessage(
      "Oops! The EcoDNA agent encountered an issue. Please try again."
    );
    console.error("Analysis error:", error);
  } finally {
    btn.disabled = false;
    btn.textContent = "Analyze Footprint";
    btn.setAttribute("aria-busy", "false");
    isSubmitting = false;
    activeController = null;
  }
});

/**
 * Show a temporary error notification.
 * @param {string} message - Error message to display.
 */
function showErrorMessage(message) {
  const existing = document.getElementById("errorNotification");
  if (existing) existing.remove();

  const notification = document.createElement("div");
  notification.id = "errorNotification";
  notification.className = "error-notification";
  notification.setAttribute("role", "alert");
  notification.textContent = message;
  document.body.appendChild(notification);

  setTimeout(() => {
    notification.remove();
  }, 5000);
}

/**
 * Render analysis results in the dashboard.
 * Uses safe DOM APIs exclusively — no innerHTML.
 *
 * @param {Object} data - API response containing footprint, recommendations, and report.
 * @param {Object} data.footprint - Carbon footprint breakdown.
 * @param {Array}  data.recommendations - List of recommendations.
 * @param {string} data.weekly_report - Formatted weekly report text.
 */
function displayResults(data) {
  // Toggle visibility
  resultsPlaceholder.classList.add("hidden");
  resultsContent.classList.remove("hidden");

  // Update score & total CO2
  document.getElementById("carbonScore").textContent = Math.round(
    data.footprint.carbon_score
  );
  document.getElementById("totalCo2").textContent =
    data.footprint.total_co2.toFixed(2);

  // ── Render breakdown list (safe DOM) ──────
  const breakdownList = document.getElementById("breakdownList");
  clearChildren(breakdownList);

  const categories = [
    { label: "Transport", value: data.footprint.transport_co2 },
    { label: "Electricity", value: data.footprint.electricity_co2 },
    { label: "Food", value: data.footprint.food_co2 },
    { label: "Shopping", value: data.footprint.shopping_co2 },
    { label: "Waste", value: data.footprint.waste_co2 },
    { label: "Water", value: data.footprint.water_co2 },
  ];

  for (const cat of categories) {
    const li = document.createElement("li");

    const nameSpan = document.createElement("span");
    nameSpan.textContent = cat.label;

    const valueSpan = document.createElement("span");
    valueSpan.textContent = `${cat.value.toFixed(2)} kg`;

    li.appendChild(nameSpan);
    li.appendChild(valueSpan);
    breakdownList.appendChild(li);
  }

  // ── Render recommendations (safe DOM) ─────
  const recsList = document.getElementById("recommendationsList");
  clearChildren(recsList);

  for (const rec of data.recommendations) {
    const li = document.createElement("li");
    li.dataset.action = rec.action;
    li.dataset.impact = rec.effort_level;
    li.setAttribute("role", "button");
    li.setAttribute("tabindex", "0");
    li.setAttribute(
      "aria-label",
      `${rec.category}: ${rec.action}. Click to track this goal.`
    );

    const strong = document.createElement("strong");
    strong.textContent = rec.category;

    const text = document.createTextNode(` ${rec.action}`);

    li.appendChild(strong);
    li.appendChild(text);

    // Click and keyboard support
    li.addEventListener("click", () => addGoal(rec.action));
    li.addEventListener("keydown", (e) => {
      if (e.key === "Enter" || e.key === " ") {
        e.preventDefault();
        addGoal(rec.action);
      }
    });

    recsList.appendChild(li);
  }

  // Type out the agent insight
  typeAgentMessage(data.weekly_report);
}

/**
 * Animate agent message with a typing effect.
 *
 * @param {string} text - Full message text to type out.
 */
function typeAgentMessage(text) {
  insightText.textContent = "";
  typingIndicator.classList.remove("hidden");

  setTimeout(() => {
    typingIndicator.classList.add("hidden");
    let i = 0;
    insightText.textContent = "";

    const interval = setInterval(() => {
      insightText.textContent += text.charAt(i);
      i++;
      if (i >= text.length) clearInterval(interval);
    }, 20);
  }, 1000);
}

/**
 * Add a new goal from a recommendation action.
 *
 * @param {string} actionText - The recommendation action to track as a goal.
 */
function addGoal(actionText) {
  if (activeGoals.find((g) => g.title === actionText)) {
    showErrorMessage("You are already tracking this goal!");
    return;
  }

  activeGoals.push({
    id: Date.now(),
    title: actionText,
    progress: Math.floor(Math.random() * 20) + 5,
  });

  saveGoals();
  renderGoals();
}

/**
 * Persist goals to localStorage.
 */
function saveGoals() {
  try {
    localStorage.setItem("ecoGoals", JSON.stringify(activeGoals));
  } catch {
    console.warn("Could not save goals to localStorage");
  }
}

/**
 * Render the active goals list using safe DOM APIs.
 */
function renderGoals() {
  goalCount.textContent = `${activeGoals.length} Active`;
  clearChildren(activeGoalsList);

  if (activeGoals.length === 0) {
    const p = document.createElement("p");
    p.className = "empty-state";
    p.textContent =
      "No goals tracked yet. Click a suggestion to start tracking!";
    activeGoalsList.appendChild(p);
    return;
  }

  for (const goal of activeGoals) {
    const card = document.createElement("div");
    card.className = "goal-card";
    card.setAttribute("role", "listitem");

    const title = document.createElement("div");
    title.className = "goal-title";
    title.textContent = goal.title;
    card.appendChild(title);

    const meta = document.createElement("div");
    meta.className = "goal-meta";

    const progressLabel = document.createElement("span");
    progressLabel.textContent = "Progress";

    const progressValue = document.createElement("span");
    progressValue.textContent = `${goal.progress}%`;

    meta.appendChild(progressLabel);
    meta.appendChild(progressValue);
    card.appendChild(meta);

    const progressTrack = document.createElement("div");
    progressTrack.className = "goal-progress";
    progressTrack.setAttribute("role", "progressbar");
    progressTrack.setAttribute("aria-valuenow", String(goal.progress));
    progressTrack.setAttribute("aria-valuemin", "0");
    progressTrack.setAttribute("aria-valuemax", "100");
    progressTrack.setAttribute(
      "aria-label",
      `Goal progress: ${goal.progress}%`
    );

    const progressBar = document.createElement("div");
    progressBar.className = "goal-progress-bar";
    progressBar.style.width = `${goal.progress}%`;

    progressTrack.appendChild(progressBar);
    card.appendChild(progressTrack);

    activeGoalsList.appendChild(card);
  }
}

/**
 * Remove all child nodes from an element.
 *
 * @param {HTMLElement} element - The element to clear.
 */
function clearChildren(element) {
  while (element.firstChild) {
    element.removeChild(element.firstChild);
  }
}
