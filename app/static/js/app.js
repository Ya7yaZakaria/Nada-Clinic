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


/* Today Clinic configured timezone clock */
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
});


/* Shared HTMX clinic interaction foundation */
window.clinicShowToast = function clinicShowToast(
    message,
    tone = "danger",
) {
    const region = document.getElementById(
        "clinic-toast-region",
    );

    if (!region || !message) {
        return;
    }

    const toastElement = document.createElement("div");

    toastElement.className = [
        "toast",
        "align-items-center",
        `text-bg-${tone}`,
        "border-0",
    ].join(" ");

    toastElement.setAttribute("role", "status");
    toastElement.setAttribute("aria-live", "polite");
    toastElement.setAttribute(
        "aria-atomic",
        "true",
    );

    toastElement.innerHTML = `
        <div class="d-flex">
            <div class="toast-body"></div>
            <button
                type="button"
                class="btn-close btn-close-white me-2 m-auto"
                data-bs-dismiss="toast"
                aria-label="Close"
            ></button>
        </div>
    `;

    toastElement.querySelector(
        ".toast-body",
    ).textContent = message;

    region.appendChild(toastElement);

    const toast = bootstrap.Toast.getOrCreateInstance(
        toastElement,
        {
            autohide: true,
            delay: 4500,
        },
    );

    toastElement.addEventListener(
        "hidden.bs.toast",
        () => {
            toastElement.remove();
        },
        { once: true },
    );

    toast.show();
};


window.clinicFormatLastUpdated =
function clinicFormatLastUpdated() {
    const liveMeta = document.getElementById(
        "clinic-live-meta",
    );
    const lastUpdated = document.getElementById(
        "clinic-last-updated",
    );

    if (!lastUpdated?.dateTime) {
        return;
    }

    const timestamp = new Date(
        lastUpdated.dateTime,
    );

    if (Number.isNaN(timestamp.getTime())) {
        return;
    }

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

    lastUpdated.textContent = formatter.format(
        timestamp,
    );
};


window.clinicOpenActionModal =
function clinicOpenActionModal() {
    const element = document.getElementById(
        "clinic-action-modal",
    );

    if (!element) {
        return;
    }

    bootstrap.Modal.getOrCreateInstance(
        element,
    ).show();
};


window.clinicCloseActionModal =
function clinicCloseActionModal() {
    const element = document.getElementById(
        "clinic-action-modal",
    );

    if (!element) {
        return;
    }

    bootstrap.Modal.getInstance(
        element,
    )?.hide();
};


window.clinicOpenDrilldown =
function clinicOpenDrilldown() {
    const element = document.getElementById(
        "clinic-drilldown-drawer",
    );

    if (!element) {
        return;
    }

    bootstrap.Offcanvas.getOrCreateInstance(
        element,
    ).show();
};


document.addEventListener(
    "DOMContentLoaded",
    () => {
        window.clinicFormatLastUpdated();
    },
);


document.body.addEventListener(
    "htmx:beforeRequest",
    (event) => {
        document.body.classList.add(
            "clinic-htmx-busy",
        );

        const indicator = document.getElementById(
            "clinic-htmx-loading",
        );

        indicator?.setAttribute(
            "aria-hidden",
            "false",
        );

        const target = event.detail.target;

        target?.setAttribute?.(
            "aria-busy",
            "true",
        );
    },
);


document.body.addEventListener(
    "htmx:afterRequest",
    (event) => {
        document.body.classList.remove(
            "clinic-htmx-busy",
        );

        const indicator = document.getElementById(
            "clinic-htmx-loading",
        );

        indicator?.setAttribute(
            "aria-hidden",
            "true",
        );

        const target = event.detail.target;

        target?.setAttribute?.(
            "aria-busy",
            "false",
        );
    },
);


document.body.addEventListener(
    "htmx:afterSwap",
    (event) => {
        const target = event.detail.target;

        if (
            target?.id
            === "clinic-action-modal-content"
        ) {
            window.clinicOpenActionModal();
        }

        if (
            target?.id
            === "clinic-drilldown-content"
        ) {
            window.clinicOpenDrilldown();
        }

        window.clinicFormatLastUpdated();
    },
);


document.body.addEventListener(
    "htmx:responseError",
    (event) => {
        const status =
            event.detail.xhr?.status || "unknown";

        window.clinicShowToast(
            `Clinic update failed (${status}). `
            + "Please try again.",
            "danger",
        );
    },
);


document.body.addEventListener(
    "htmx:sendError",
    () => {
        window.clinicShowToast(
            "Network error. The clinic update "
            + "was not completed.",
            "danger",
        );
    },
);


document.body.addEventListener(
    "clinic:action-success",
    (event) => {
        window.clinicCloseActionModal();

        window.clinicShowToast(
            event.detail?.message
            || "Clinic updated.",
            event.detail?.tone || "success",
        );
    },
);
