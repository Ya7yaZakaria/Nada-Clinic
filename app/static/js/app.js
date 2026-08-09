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
        if (event.detail.target?.id === "today-clinic-dynamic") {
            window.clinicTodayState.scrollY = window.scrollY;
        }
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
        window.clinicInitTodayControls();

        if (target?.id === "today-clinic-dynamic") {
            window.requestAnimationFrame(() => {
                window.scrollTo({
                    top: window.clinicTodayState.scrollY,
                    behavior: "auto",
                });
            });
        }
    },
);

/* Today's Clinic local search, focused filters and sorting. */
window.clinicTodayState = window.clinicTodayState || {
    search: "",
    status: "all",
    type: "all",
    quick: "all",
    sort: "time",
    scrollY: 0,
};

window.clinicApplyTodayControls = function clinicApplyTodayControls() {
    const root = document.getElementById("today-clinic-dynamic");

    if (!root) {
        return;
    }

    const state = window.clinicTodayState;
    const cards = Array.from(root.querySelectorAll("[data-clinic-patient-card]"));
    let visible = 0;

    cards.forEach((card) => {
        const haystack = [card.dataset.name, card.dataset.mrn, card.dataset.phone]
            .join(" ")
            .toLocaleLowerCase();
        const queryMatches = !state.search || haystack.includes(state.search);
        const cardStatus = card.dataset.status;
        const statusMatches = state.status === "all"
            || cardStatus === state.status
            || (state.status === "remaining" && ["booked", "waiting"].includes(cardStatus))
            || (state.status === "resolved" && ["completed", "cancelled"].includes(cardStatus));
        const typeMatches = state.type === "all" || card.dataset.type === state.type;
        const quickMatches = state.quick === "all"
            || (state.quick === "emergency" && card.dataset.emergency === "true")
            || (state.quick === "delayed" && card.dataset.delayed === "true");
        const show = queryMatches && statusMatches && typeMatches && quickMatches;

        card.hidden = !show;
        if (show) {
            visible += 1;
        }
    });

    root.querySelectorAll("[data-clinic-sort-container]").forEach((container) => {
        const sortedCards = Array.from(container.querySelectorAll("[data-clinic-patient-card]"));

        sortedCards.sort((left, right) => {
            if (state.sort === "wait") {
                return Number(right.dataset.waitMinutes) - Number(left.dataset.waitMinutes);
            }
            if (state.sort === "name") {
                return left.dataset.name.localeCompare(right.dataset.name);
            }
            return left.dataset.time.localeCompare(right.dataset.time);
        });

        sortedCards.forEach((card) => container.appendChild(card));
    });

    const count = document.getElementById("clinic-visible-count");
    if (count) {
        count.textContent = `${visible} patient${visible === 1 ? "" : "s"} shown`;
    }

    root.querySelectorAll("[data-clinic-kpi-filter]").forEach((button) => {
        button.setAttribute("aria-pressed", String(button.dataset.clinicKpiFilter === state.status));
    });
    root.querySelectorAll("[data-clinic-quick-filter]").forEach((button) => {
        button.classList.toggle("active", button.dataset.clinicQuickFilter === state.quick);
    });
};

window.clinicInitTodayControls = function clinicInitTodayControls() {
    const root = document.getElementById("today-clinic-dynamic");
    if (!root) {
        return;
    }

    const state = window.clinicTodayState;
    const search = document.getElementById("clinic-list-search");
    const status = document.getElementById("clinic-status-filter");
    const type = document.getElementById("clinic-type-filter");
    const sort = document.getElementById("clinic-list-sort");

    if (search) search.value = state.search;
    if (status) status.value = state.status;
    if (type) type.value = state.type;
    if (sort) sort.value = state.sort;
    window.clinicApplyTodayControls();
};

document.body.addEventListener("input", (event) => {
    if (event.target.id !== "clinic-list-search") return;
    window.clinicTodayState.search = event.target.value.trim().toLocaleLowerCase();
    window.clinicApplyTodayControls();
});

document.body.addEventListener("change", (event) => {
    const stateKey = {
        "clinic-status-filter": "status",
        "clinic-type-filter": "type",
        "clinic-list-sort": "sort",
    }[event.target.id];
    if (!stateKey) return;
    window.clinicTodayState[stateKey] = event.target.value;
    window.clinicApplyTodayControls();
});

document.body.addEventListener("click", (event) => {
    const kpi = event.target.closest("[data-clinic-kpi-filter]");
    const quick = event.target.closest("[data-clinic-quick-filter]");
    const clear = event.target.closest("[data-clinic-clear-filters]");

    if (kpi) {
        window.clinicTodayState.status = kpi.dataset.clinicKpiFilter;
        window.clinicTodayState.quick = "all";
        window.clinicInitTodayControls();
        document.querySelector(".clinic-operational-columns")?.scrollIntoView({ behavior: "smooth", block: "start" });
    } else if (quick) {
        const selected = quick.dataset.clinicQuickFilter;
        window.clinicTodayState.quick = window.clinicTodayState.quick === selected ? "all" : selected;
        window.clinicApplyTodayControls();
    } else if (clear) {
        Object.assign(window.clinicTodayState, { search: "", status: "all", type: "all", quick: "all", sort: "time" });
        window.clinicInitTodayControls();
    }
});

document.addEventListener("DOMContentLoaded", window.clinicInitTodayControls);


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

        htmx.trigger(
            document.body,
            "clinicSync",
        );
    },
);

/* Today Clinic Patient card workspace navigation */
function clinicOpenPatientWorkspaceCard(card) {
    const workspaceUrl = card?.dataset.workspaceUrl;

    if (workspaceUrl) {
        window.location.assign(workspaceUrl);
    }
}


document.body.addEventListener(
    "click",
    (event) => {
        const card = event.target.closest(
            ".clinic-patient-card[data-workspace-url]",
        );

        if (!card) {
            return;
        }

        const interactiveElement = event.target.closest(
            "a, button, form, input, select, textarea, "
            + "label, summary, [role='button']",
        );

        if (interactiveElement) {
            return;
        }

        clinicOpenPatientWorkspaceCard(card);
    },
);


document.body.addEventListener(
    "keydown",
    (event) => {
        if (
            event.key !== "Enter"
            && event.key !== " "
        ) {
            return;
        }

        const card = event.target.closest(
            ".clinic-patient-card[data-workspace-url]",
        );

        if (!card || event.target !== card) {
            return;
        }

        event.preventDefault();
        clinicOpenPatientWorkspaceCard(card);
    },
);

/* Today Clinic mobile disclosure polish */
window.clinicInitMobileDisclosures =
function clinicInitMobileDisclosures() {
    const compactViewport = window.matchMedia(
        "(max-width: 575.98px)",
    ).matches;

    document.querySelectorAll(
        "[data-clinic-mobile-collapse]",
    ).forEach((section) => {
        if (section.dataset.clinicDisclosureReady === "true") {
            return;
        }

        section.open = !compactViewport;
        section.dataset.clinicDisclosureReady = "true";
    });
};


document.addEventListener(
    "DOMContentLoaded",
    window.clinicInitMobileDisclosures,
);


document.body.addEventListener(
    "htmx:afterSwap",
    () => {
        window.clinicInitMobileDisclosures();
    },
);
