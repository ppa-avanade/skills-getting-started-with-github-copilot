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
        ? `<ul class="participants-list">${activity.participants.map((email) => `<li>
            <span class="participant-email">${email}</span>
            <button class="delete-participant" onclick="removeParticipant('${name}', '${email}')" title="Supprimer ce participant">✕</button>
          </li>`).join("")}</ul>`
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
  const submitButton = event.target.querySelector('button[type="submit"]');
  const originalButtonText = submitButton.textContent;

  // Disable button and show loading state
  submitButton.disabled = true;
  submitButton.textContent = "Inscription en cours...";

  try {
    const response = await fetch(
      `/activities/${encodeURIComponent(activity)}/signup?email=${encodeURIComponent(email)}`,
      {
        method: "POST",
      }
    );

    if (response.ok) {
      const result = await response.json();
      
      // Show success message
      showMessage("success", result.message);
      
      // Reset form
      document.getElementById("signup-form").reset();
      
      // Show loading indicator while refreshing activities
      const activitiesList = document.getElementById("activities-list");
      const originalContent = activitiesList.innerHTML;
      activitiesList.innerHTML = '<p class="loading">Mise à jour des activités...</p>';
      
      // Reload activities and wait for completion
      await loadActivities();
      
      // Additional visual feedback that update is complete
      showMessage("info", "Liste des activités mise à jour !");
      
    } else {
      const error = await response.json();
      showMessage("error", error.detail);
    }
  } catch (error) {
    showMessage("error", "Une erreur est survenue lors de l'inscription.");
    console.error("Signup error:", error);
  } finally {
    // Re-enable button
    submitButton.disabled = false;
    submitButton.textContent = originalButtonText;
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

async function removeParticipant(activityName, email) {
  if (!confirm(`Êtes-vous sûr de vouloir supprimer ${email} de l'activité "${activityName}" ?`)) {
    return;
  }

  try {
    // Show loading indicator
    const activitiesList = document.getElementById("activities-list");
    const originalContent = activitiesList.innerHTML;
    activitiesList.innerHTML = '<p class="loading">Suppression en cours...</p>';

    const response = await fetch(
      `/activities/${encodeURIComponent(activityName)}/remove?email=${encodeURIComponent(email)}`,
      {
        method: "DELETE",
      }
    );

    if (response.ok) {
      const result = await response.json();
      showMessage("success", result.message);
      
      // Reload activities and wait for completion
      await loadActivities();
      
      // Additional confirmation that update is complete
      showMessage("info", "Liste des participants mise à jour !");
      
    } else {
      // Restore original content on error
      activitiesList.innerHTML = originalContent;
      const error = await response.json();
      showMessage("error", error.detail);
    }
  } catch (error) {
    // Restore original content on error
    const activitiesList = document.getElementById("activities-list");
    if (activitiesList.innerHTML.includes("Suppression en cours...")) {
      await loadActivities(); // Reload to restore proper state
    }
    showMessage("error", "Une erreur est survenue lors de la suppression.");
    console.error("Remove participant error:", error);
  }
}
