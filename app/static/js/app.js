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
