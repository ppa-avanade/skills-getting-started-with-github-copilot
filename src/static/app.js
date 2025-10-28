document.addEventListener("DOMContentLoaded", () => {
  loadActivities();

  document.getElementById("signup-form").addEventListener("submit", handleSignup);
});

async function loadActivities() {
  try {
    const response = await fetch("/activities");
    const activities = await response.json();

    displayActivities(activities);
    populateActivitySelect(activities);
  } catch (error) {
    console.error("Error loading activities:", error);
    document.getElementById("activities-list").innerHTML = '<p class="error">Failed to load activities.</p>';
  }
}

function displayActivities(activities) {
  const activitiesList = document.getElementById("activities-list");
  activitiesList.innerHTML = "";

  for (const [name, activity] of Object.entries(activities)) {
    const activityCard = document.createElement("div");
    activityCard.className = "activity-card";

    const participantsHtml =
      activity.participants && activity.participants.length > 0
        ? `<ul class="participants-list">${activity.participants.map((email) => `<li>${email}</li>`).join("")}</ul>`
        : '<p class="no-participants">Aucun participant inscrit</p>';

    activityCard.innerHTML = `
            <h4>${name}</h4>
            <p><strong>Description:</strong> ${activity.description}</p>
            <p><strong>Horaire:</strong> ${activity.schedule}</p>
            <p><strong>Places disponibles:</strong> ${activity.max_participants - activity.participants.length}/${activity.max_participants}</p>
            <div class="participants-section">
                <h5>Participants inscrits:</h5>
                ${participantsHtml}
            </div>
        `;

    activitiesList.appendChild(activityCard);
  }
}

function populateActivitySelect(activities) {
  const activitySelect = document.getElementById("activity");
  activitySelect.innerHTML = '<option value="">-- Sélectionnez une activité --</option>';

  for (const name of Object.keys(activities)) {
    const option = document.createElement("option");
    option.value = name;
    option.textContent = name;
    activitySelect.appendChild(option);
  }
}

async function handleSignup(event) {
  event.preventDefault();

  const email = document.getElementById("email").value;
  const activity = document.getElementById("activity").value;
  const messageDiv = document.getElementById("message");

  try {
    const response = await fetch(
      `/activities/${encodeURIComponent(activity)}/signup?email=${encodeURIComponent(email)}`,
      {
        method: "POST",
      }
    );

    if (response.ok) {
      const result = await response.json();
      showMessage("success", result.message);
      document.getElementById("signup-form").reset();
      loadActivities(); // Reload to show updated participants
    } else {
      const error = await response.json();
      showMessage("error", error.detail);
    }
  } catch (error) {
    showMessage("error", "Une erreur est survenue lors de l'inscription.");
    console.error("Signup error:", error);
  }
}

function showMessage(type, text) {
  const messageDiv = document.getElementById("message");
  messageDiv.className = `message ${type}`;
  messageDiv.textContent = text;
  messageDiv.classList.remove("hidden");

  setTimeout(() => {
    messageDiv.classList.add("hidden");
  }, 5000);
}
