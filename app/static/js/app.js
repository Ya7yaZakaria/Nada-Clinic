document.documentElement.classList.add("clinic-ui-ready");

/* Application shell interaction */
window.clinicShell = function clinicShell() {
    let collapseTimer = null;

    return {
        sidebarOpen: false,
        sidebarPinned:
            localStorage.getItem(
                "clinicSidebarPinned"
            ) === "true",
        sidebarHovered: false,
        sidebarFocused: false,

        get sidebarExpanded() {
            return (
                this.sidebarPinned
                || this.sidebarHovered
                || this.sidebarFocused
            );
        },

        clearCollapseTimer() {
            if (collapseTimer !== null) {
                window.clearTimeout(collapseTimer);
                collapseTimer = null;
            }
        },

        enterSidebar() {
            this.clearCollapseTimer();
            this.sidebarHovered = true;
        },

        leaveSidebar() {
            this.clearCollapseTimer();

            collapseTimer = window.setTimeout(() => {
                this.sidebarHovered = false;
                collapseTimer = null;
            }, 280);
        },

        focusSidebar() {
            this.clearCollapseTimer();
            this.sidebarFocused = true;
        },

        blurSidebar(event) {
            const nextTarget = event.relatedTarget;

            if (
                nextTarget
                && event.currentTarget.contains(nextTarget)
            ) {
                return;
            }

            this.sidebarFocused = false;
        },

        toggleSidebarPin() {
            this.clearCollapseTimer();
            this.sidebarPinned = !this.sidebarPinned;
            this.sidebarHovered = false;

            localStorage.setItem(
                "clinicSidebarPinned",
                String(this.sidebarPinned),
            );
        },

        closeMobileSidebar() {
            this.sidebarOpen = false;
        },
    };
};


/* Today Clinic configured timezone clock and refresh */
document.addEventListener("DOMContentLoaded", () => {
    const liveMeta = document.getElementById(
        "clinic-live-meta",
    );
    const clock = document.getElementById(
        "clinic-live-clock",
    );
    const lastUpdated = document.getElementById(
        "clinic-last-updated",
    );
    const refreshButton = document.getElementById(
        "clinic-manual-refresh",
    );

    const configuredTimezone =
        liveMeta?.dataset.timezone || "Africa/Cairo";

    let formatter;

    try {
        formatter = new Intl.DateTimeFormat(
            undefined,
            {
                timeZone: configuredTimezone,
                hour: "2-digit",
                minute: "2-digit",
                second: "2-digit",
                hour12: false,
            },
        );
    } catch (error) {
        console.warn(
            "Invalid configured timezone; using device timezone.",
            configuredTimezone,
            error,
        );

        formatter = new Intl.DateTimeFormat(
            undefined,
            {
                hour: "2-digit",
                minute: "2-digit",
                second: "2-digit",
                hour12: false,
            },
        );
    }

    if (clock) {
        const updateClock = () => {
            clock.textContent = formatter.format(
                new Date(),
            );
        };

        updateClock();
        window.setInterval(updateClock, 1000);
    }

    if (lastUpdated?.dateTime) {
        const timestamp = new Date(
            lastUpdated.dateTime,
        );

        if (!Number.isNaN(timestamp.getTime())) {
            lastUpdated.textContent =
                formatter.format(timestamp);
        }
    }

    if (refreshButton) {
        refreshButton.addEventListener(
            "click",
            () => {
                window.location.reload();
            },
        );
    }
});
