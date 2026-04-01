document.addEventListener("DOMContentLoaded", () => {
  const activitiesList = document.getElementById("activities-list");
  const activitySelect = document.getElementById("activity");
  const scheduleBlocks = document.getElementById("schedule-blocks");
  const signupForm = document.getElementById("signup-form");
  const messageDiv = document.getElementById("message");

  function formatTime(time) {
    const [hours, minutes] = time.split(":").map(Number);
    const suffix = hours >= 12 ? "PM" : "AM";
    const normalizedHours = hours % 12 || 12;
    return `${normalizedHours}:${String(minutes).padStart(2, "0")} ${suffix}`;
  }

  function renderTimeSlots(timeSlots) {
    if (!timeSlots?.length) {
      return "<p><em>No structured time slots yet</em></p>";
    }

    return `
      <div class="time-slots">
        ${timeSlots
          .map(
            (slot) => `
              <span class="time-slot-pill">
                ${slot.day} ${formatTime(slot.start_time)} - ${formatTime(slot.end_time)}
              </span>
            `
          )
          .join("")}
      </div>
    `;
  }

  function renderConflicts(conflicts) {
    if (!conflicts?.length) {
      return '<p class="conflict-status ok">No overlapping activities</p>';
    }

    return `
      <div class="conflict-status warning">
        <strong>Conflicts with:</strong> ${conflicts.join(", ")}
      </div>
    `;
  }

  async function fetchScheduleBlocks() {
    try {
      const response = await fetch("/schedule/blocks");
      const blocks = await response.json();

      scheduleBlocks.innerHTML = `
        <div class="schedule-block-list">
          ${blocks
            .map(
              (block) => `
                <div class="schedule-block-card">
                  <h4>${block.name}</h4>
                  <p>${formatTime(block.start_time)} - ${formatTime(block.end_time)}</p>
                </div>
              `
            )
            .join("")}
        </div>
      `;
    } catch (error) {
      scheduleBlocks.innerHTML =
        "<p>Failed to load school day blocks. Please try again later.</p>";
      console.error("Error fetching school day blocks:", error);
    }
  }

  // Function to fetch activities from API
  async function fetchActivities() {
    try {
      const response = await fetch("/activities");
      const activities = await response.json();

      // Clear loading message
      activitiesList.innerHTML = "";
      activitySelect.innerHTML = '<option value="">-- Select an activity --</option>';

      // Populate activities list
      Object.entries(activities).forEach(([name, details]) => {
        const activityCard = document.createElement("div");
        activityCard.className = "activity-card";

        // Create participants HTML with delete icons instead of bullet points
        const participantsHTML =
          details.participants.length > 0
            ? `<div class="participants-section">
              <h5>Participants:</h5>
              <ul class="participants-list">
                ${details.participants
                  .map(
                    (email) =>
                      `<li><span class="participant-email">${email}</span><button class="delete-btn" data-activity="${name}" data-email="${email}">❌</button></li>`
                  )
                  .join("")}
              </ul>
            </div>`
            : `<p><em>No participants yet</em></p>`;

        activityCard.innerHTML = `
          <h4>${name}</h4>
          <p>${details.description}</p>
          <p><strong>Schedule:</strong> ${details.schedule}</p>
          <p><strong>Structured Time Slots:</strong></p>
          ${renderTimeSlots(details.time_slots)}
          <p><strong>Availability:</strong> ${details.availability} (${details.spots_left} spots left)</p>
          ${renderConflicts(details.conflicts_with)}
          <div class="participants-container">
            ${participantsHTML}
          </div>
        `;

        activitiesList.appendChild(activityCard);

        // Add option to select dropdown
        const option = document.createElement("option");
        option.value = name;
        option.textContent = name;
        activitySelect.appendChild(option);
      });

      // Add event listeners to delete buttons
      document.querySelectorAll(".delete-btn").forEach((button) => {
        button.addEventListener("click", handleUnregister);
      });
    } catch (error) {
      activitiesList.innerHTML =
        "<p>Failed to load activities. Please try again later.</p>";
      console.error("Error fetching activities:", error);
    }
  }

  // Handle unregister functionality
  async function handleUnregister(event) {
    const button = event.target;
    const activity = button.getAttribute("data-activity");
    const email = button.getAttribute("data-email");

    try {
      const response = await fetch(
        `/activities/${encodeURIComponent(
          activity
        )}/unregister?email=${encodeURIComponent(email)}`,
        {
          method: "DELETE",
        }
      );

      const result = await response.json();

      if (response.ok) {
        messageDiv.textContent = result.message;
        messageDiv.className = "success";

        // Refresh activities list to show updated participants
        fetchActivities();
      } else {
        messageDiv.textContent = result.detail || "An error occurred";
        messageDiv.className = "error";
      }

      messageDiv.classList.remove("hidden");

      // Hide message after 5 seconds
      setTimeout(() => {
        messageDiv.classList.add("hidden");
      }, 5000);
    } catch (error) {
      messageDiv.textContent = "Failed to unregister. Please try again.";
      messageDiv.className = "error";
      messageDiv.classList.remove("hidden");
      console.error("Error unregistering:", error);
    }
  }

  // Handle form submission
  signupForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const email = document.getElementById("email").value;
    const activity = document.getElementById("activity").value;

    try {
      const response = await fetch(
        `/activities/${encodeURIComponent(
          activity
        )}/signup?email=${encodeURIComponent(email)}`,
        {
          method: "POST",
        }
      );

      const result = await response.json();

      if (response.ok) {
        messageDiv.textContent = result.message;
        messageDiv.className = "success";
        signupForm.reset();

        // Refresh activities list to show updated participants
        fetchActivities();
      } else {
        messageDiv.textContent = result.detail || "An error occurred";
        messageDiv.className = "error";
      }

      messageDiv.classList.remove("hidden");

      // Hide message after 5 seconds
      setTimeout(() => {
        messageDiv.classList.add("hidden");
      }, 5000);
    } catch (error) {
      messageDiv.textContent = "Failed to sign up. Please try again.";
      messageDiv.className = "error";
      messageDiv.classList.remove("hidden");
      console.error("Error signing up:", error);
    }
  });

  // Initialize app
  fetchScheduleBlocks();
  fetchActivities();
});
