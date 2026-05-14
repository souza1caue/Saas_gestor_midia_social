document.addEventListener("DOMContentLoaded", () => {
    const alerts = document.querySelectorAll(".alert");
    alerts.forEach((alert) => {
        setTimeout(() => alert.classList.add("fade"), 3500);
    });

    const eventModal = document.getElementById("eventModal");
    if (eventModal) {
        eventModal.addEventListener("show.bs.modal", (event) => {
            const button = event.relatedTarget;
            const date = button?.getAttribute("data-date");
            const eventDateInput = document.getElementById("eventDateInput");
            const eventDateDisplay = document.getElementById("eventDateDisplay");

            if (date && eventDateInput && eventDateDisplay) {
                const [year, month, day] = date.split("-");
                eventDateInput.value = date;
                eventDateDisplay.value = `${day}/${month}/${year}`;
            }
        });
    }
});
