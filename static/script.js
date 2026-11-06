/* ==========================================================================
   Student Management System - Interactive Frontend Script (Vanilla JS)
   ========================================================================== */

document.addEventListener("DOMContentLoaded", function () {

    // 1. Live Digital Clock & Formatted Today's Date in Top Navbar
    const clockElement = document.getElementById("live-clock");
    const dateElement = document.getElementById("current-date");

    function updateClockAndDate() {
        const now = new Date();

        if (clockElement) {
            clockElement.textContent = now.toLocaleTimeString("en-US", {
                hour: "2-digit",
                minute: "2-digit",
                second: "2-digit",
                hour12: true
            });
        }

        if (dateElement) {
            dateElement.textContent = now.toLocaleDateString("en-US", {
                weekday: "short",
                year: "numeric",
                month: "short",
                day: "numeric"
            });
        }
    }

    if (clockElement || dateElement) {
        updateClockAndDate();
        setInterval(updateClockAndDate, 1000);
    }

    // 2. Show / Hide Password Toggle on Login Page
    const togglePasswordBtn = document.getElementById("toggle-password");
    const passwordInput = document.getElementById("password");

    if (togglePasswordBtn && passwordInput) {
        togglePasswordBtn.addEventListener("click", function () {
            const isPassword = passwordInput.getAttribute("type") === "password";
            passwordInput.setAttribute("type", isPassword ? "text" : "password");

            const icon = togglePasswordBtn.querySelector("i");
            if (icon) {
                icon.className = isPassword ? "fa-regular fa-eye-slash" : "fa-regular fa-eye";
            }
            togglePasswordBtn.setAttribute(
                "aria-label",
                isPassword ? "Hide password" : "Show password"
            );
        });
    }

    // 3. Instant Table Search & Filtering (Students, Attendance, Marks, Reports)
    const searchInputs = document.querySelectorAll("[data-search-target]");

    searchInputs.forEach(function (input) {
        const targetTableId = input.getAttribute("data-search-target");
        const table = document.getElementById(targetTableId);
        if (!table) return;

        const tbody = table.querySelector("tbody");
        const noMatchRow = table.querySelector(".no-search-results");

        input.addEventListener("input", function () {
            const query = input.value.toLowerCase().trim();
            const rows = tbody.querySelectorAll("tr.data-row");
            let visibleCount = 0;

            rows.forEach(function (row) {
                const text = row.textContent.toLowerCase();
                if (text.includes(query)) {
                    row.style.display = "";
                    visibleCount++;
                } else {
                    row.style.display = "none";
                }
            });

            if (noMatchRow) {
                noMatchRow.style.display = (rows.length > 0 && visibleCount === 0) ? "" : "none";
            }
        });
    });

    // 4. Mobile Sidebar Menu Toggle
    const mobileMenuBtn = document.getElementById("mobile-menu-btn");
    const sidebar = document.getElementById("sidebar");

    if (mobileMenuBtn && sidebar) {
        mobileMenuBtn.addEventListener("click", function () {
            sidebar.classList.toggle("open");
        });
    }

    // 5. Dismissible Alert Notifications
    const closeButtons = document.querySelectorAll(".alert-close-btn");
    closeButtons.forEach(function (btn) {
        btn.addEventListener("click", function () {
            const alertBox = btn.closest(".alert-banner, .success, .error");
            if (alertBox) {
                alertBox.style.display = "none";
            }
        });
    });
});
