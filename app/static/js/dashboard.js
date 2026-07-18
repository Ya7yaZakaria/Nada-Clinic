(function () {
    "use strict";

    function currentTimeText(now) {
        return new Intl.DateTimeFormat(
            undefined,
            {
                hour: "2-digit",
                minute: "2-digit",
                hour12: true,
            }
        ).format(now);
    }

    function currentDateText(now) {
        return new Intl.DateTimeFormat(
            undefined,
            {
                weekday: "long",
                day: "2-digit",
                month: "long",
                year: "numeric",
            }
        ).format(now);
    }

    function updateLiveContext() {
        const now = new Date();
        const hour = now.getHours();

        const clock = document.getElementById(
            "dashboard-live-clock"
        );

        const dateNode = document.getElementById(
            "dashboard-live-date"
        );

        const greeting = document.getElementById(
            "dashboard-greeting"
        );

        const todayClock = document.getElementById(
            "today-clinic-live-time"
        );

        const timeText = currentTimeText(now);

        if (clock) {
            clock.textContent = timeText;
            clock.dateTime = now.toISOString();
        }

        if (todayClock) {
            todayClock.textContent = timeText;
        }

        if (dateNode) {
            dateNode.textContent = currentDateText(
                now
            );
        }

        if (greeting) {
            if (hour < 12) {
                greeting.textContent = "morning";
            } else if (hour < 18) {
                greeting.textContent = "afternoon";
            } else {
                greeting.textContent = "evening";
            }
        }
    }

    function readChartData() {
        const node = document.getElementById(
            "dashboard-chart-data"
        );

        if (!node) {
            return null;
        }

        try {
            return JSON.parse(
                node.textContent
            );
        } catch (error) {
            console.error(
                "Invalid dashboard chart data.",
                error
            );
            return null;
        }
    }

    function cartesianOptions() {
        return {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                mode: "index",
                intersect: false,
            },
            plugins: {
                legend: {
                    position: "bottom",
                    labels: {
                        usePointStyle: true,
                    },
                },
            },
            scales: {
                x: {
                    grid: {
                        display: false,
                    },
                },
                y: {
                    beginAtZero: true,
                    ticks: {
                        precision: 0,
                    },
                },
            },
        };
    }

    function doughnutOptions() {
        return {
            responsive: true,
            maintainAspectRatio: false,
            cutout: "68%",
            plugins: {
                legend: {
                    position: "bottom",
                    labels: {
                        usePointStyle: true,
                    },
                },
            },
        };
    }

    const initializedCanvases = new WeakSet();

    function hasValues(dataset) {
        return dataset
            && Array.isArray(dataset.values)
            && dataset.values.some(function (value) {
                return Number(value) !== 0;
            });
    }

    function renderSimpleChart(id, dataset, type, colors) {
        const canvas = document.getElementById(id);
        if (!canvas || initializedCanvases.has(canvas) || !hasValues(dataset)) {
            return;
        }
        initializedCanvases.add(canvas);
        new Chart(canvas, {
            type: type,
            data: {
                labels: dataset.labels,
                datasets: [{
                    data: dataset.values,
                    backgroundColor: colors,
                    borderWidth: 0,
                    borderRadius: type === "bar" ? 6 : 0,
                }],
            },
            options: type === "doughnut" ? doughnutOptions() : cartesianOptions(),
        });
    }

    function initializeCharts(data) {
        if (
            !data
            || typeof window.Chart === "undefined"
        ) {
            return;
        }

        const activityCanvas =
            document.getElementById(
                "dashboard-activity-chart"
            );

        if (
            activityCanvas
            && data.activity
            && !initializedCanvases.has(activityCanvas)
        ) {
            const activityDatasets = [];

            if (
                Array.isArray(
                    data.activity.appointments
                )
            ) {
                activityDatasets.push(
                    {
                        label: "Appointments",
                        data:
                            data.activity
                                .appointments,
                        borderColor:
                            "#0d6efd",
                        backgroundColor:
                            "rgba(13,110,253,.12)",
                        fill: true,
                        tension: 0.35,
                    }
                );
            }

            if (
                Array.isArray(
                    data.activity.visits
                )
            ) {
                activityDatasets.push(
                    {
                        label: "Visits",
                        data:
                            data.activity.visits,
                        borderColor:
                            "#6f42c1",
                        backgroundColor:
                            "rgba(111,66,193,.08)",
                        fill: true,
                        tension: 0.35,
                    }
                );
            }

            if (
                Array.isArray(
                    data.activity.new_patients
                )
            ) {
                activityDatasets.push(
                    {
                        label: "New Patients",
                        data:
                            data.activity
                                .new_patients,
                        borderColor:
                            "#198754",
                        backgroundColor:
                            "rgba(25,135,84,.08)",
                        fill: true,
                        tension: 0.35,
                    }
                );
            }

            if (activityDatasets.length > 0) {
                initializedCanvases.add(activityCanvas);
                new Chart(
                    activityCanvas,
                    {
                        type: "line",
                        data: {
                            labels:
                                data.activity.labels,
                            datasets:
                                activityDatasets,
                        },
                        options:
                            cartesianOptions(),
                    }
                );
            }
        }

        const journeyCanvas =
            document.getElementById(
                "dashboard-journey-chart"
            );

        if (
            journeyCanvas
            && hasValues(data.journeys)
            && !initializedCanvases.has(journeyCanvas)
        ) {
            initializedCanvases.add(journeyCanvas);
            new Chart(
                journeyCanvas,
                {
                    type: "doughnut",
                    data: {
                        labels:
                            data.journeys.labels,
                        datasets: [
                            {
                                data:
                                    data.journeys
                                        .values,
                                backgroundColor: [
                                    "#20c997",
                                    "#6f42c1",
                                    "#fd7e14",
                                ],
                                borderWidth: 0,
                            },
                        ],
                    },
                    options:
                        doughnutOptions(),
                }
            );
        }

        const financeCanvas =
            document.getElementById(
                "dashboard-finance-chart"
            );

        if (
            financeCanvas
            && data.finance
            && !initializedCanvases.has(financeCanvas)
            && [data.finance.revenue, data.finance.expenses].flat().some(function (value) { return Number(value) !== 0; })
        ) {
            initializedCanvases.add(financeCanvas);
            new Chart(
                financeCanvas,
                {
                    type: "bar",
                    data: {
                        labels:
                            data.finance.labels,
                        datasets: [
                            {
                                label: "Revenue",
                                data:
                                    data.finance
                                        .revenue,
                                backgroundColor:
                                    "rgba(25,135,84,.72)",
                                borderRadius: 6,
                            },
                            {
                                label:
                                    "Expenses",
                                data:
                                    data.finance
                                        .expenses,
                                backgroundColor:
                                    "rgba(220,53,69,.62)",
                                borderRadius: 6,
                            },
                        ],
                    },
                    options:
                        cartesianOptions(),
                }
            );
        }

        const appointmentCanvas =
            document.getElementById(
                "dashboard-appointment-chart"
            );

        if (
            appointmentCanvas
            && hasValues(data.appointments)
            && !initializedCanvases.has(appointmentCanvas)
        ) {
            initializedCanvases.add(appointmentCanvas);
            new Chart(
                appointmentCanvas,
                {
                    type: "doughnut",
                    data: {
                        labels:
                            data.appointments
                                .labels,
                        datasets: [
                            {
                                data:
                                    data.appointments
                                        .values,
                                backgroundColor: [
                                    "#0d6efd",
                                    "#ffc107",
                                    "#198754",
                                    "#dc3545",
                                    "#6c757d",
                                    "#fd7e14",
                                ],
                                borderWidth: 0,
                            },
                        ],
                    },
                    options:
                        doughnutOptions(),
                }
            );
        }

        renderSimpleChart("dashboard-visit-types-chart", data.visit_types, "bar", "rgba(111,66,193,.72)");
        renderSimpleChart("dashboard-revenue-services-chart", data.revenue_services, "bar", "rgba(25,135,84,.72)");
        renderSimpleChart("dashboard-appointment-types-chart", data.appointment_types, "doughnut", ["#0d6efd", "#20c997", "#dc3545"]);
        renderSimpleChart("dashboard-appointment-sources-chart", data.appointment_sources, "doughnut", ["#6f42c1", "#198754", "#0dcaf0", "#fd7e14"]);
        renderSimpleChart("dashboard-ultrasound-types-chart", data.ultrasound_types, "doughnut", ["#0d6efd", "#d63384", "#20c997", "#6c757d"]);
        renderSimpleChart("dashboard-surgery-statuses-chart", data.surgery_statuses, "doughnut", ["#0d6efd", "#198754", "#dc3545", "#ffc107"]);
    }

    document.addEventListener(
        "DOMContentLoaded",
        function () {
            updateLiveContext();

            window.setInterval(
                updateLiveContext,
                60000
            );

            initializeCharts(
                readChartData()
            );
        }
    );
})();
