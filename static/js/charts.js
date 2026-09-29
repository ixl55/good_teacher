/* ===================== الرسوم البيانية باستخدام Chart.js ===================== */
const _chartInstances = {};
const _chartRenderers = {};

function _cssVar(name, fallback) {
    const v = getComputedStyle(document.documentElement).getPropertyValue(name).trim();
    return v || fallback;
}

function _theme() {
    return {
        series: _cssVar("--chart-series", "#2a78d6"),
        grid: _cssVar("--chart-grid", "#e1e0d9"),
        axis: _cssVar("--chart-axis", "#c3c2b7"),
        surface: _cssVar("--chart-surface", "#ffffff"),
        text: _cssVar("--text", "#161615"),
        muted: _cssVar("--text-muted", "#5b5a56"),
        faint: _cssVar("--text-faint", "#8a8984"),
        tooltipBg: _cssVar("--bg-elevated", "#ffffff"),
        border: _cssVar("--border-strong", "rgba(0,0,0,.16)"),
    };
}

function _withAlpha(hex, alpha) {
    const h = hex.replace("#", "");
    if (h.length !== 6) return hex;
    const n = parseInt(h, 16);
    return `rgba(${(n >> 16) & 255}, ${(n >> 8) & 255}, ${n & 255}, ${alpha})`;
}

function _baseOptions(th, opts) {
    const font = { family: getComputedStyle(document.body).fontFamily, size: 12 };
    return {
        responsive: true,
        maintainAspectRatio: false,
        animation: { duration: 350 },
        layout: { padding: { top: opts.topPadding || 8 } },
        plugins: {
            legend: { display: false },
            tooltip: {
                rtl: IS_RTL,
                textDirection: IS_RTL ? "rtl" : "ltr",
                backgroundColor: th.tooltipBg,
                titleColor: th.text,
                bodyColor: th.muted,
                borderColor: th.border,
                borderWidth: 1,
                padding: 10,
                cornerRadius: 8,
                displayColors: false,
                titleFont: { ...font, size: 13, weight: "600" },
                bodyFont: { ...font, size: 13 },
                callbacks: {
                    label: (ctx) => ctx.parsed.y === null ? t("no_grade") : `${opts.valueLabel || t("grade")}: ${formatNumber(ctx.parsed.y)}`,
                },
            },
        },
        scales: {
            y: {
                min: 0,
                max: opts.max ?? 100,
                position: IS_RTL ? "right" : "left",
                grid: { color: th.grid, lineWidth: 1, drawTicks: false },
                border: { display: false },
                ticks: { color: th.faint, font, padding: 8, stepSize: 20 },
            },
            x: {
                reverse: IS_RTL, // في العربية: الزمن والترتيب يسيران من اليمين لليسار
                grid: { display: false },
                border: { color: th.axis },
                ticks: { color: th.faint, font, autoSkip: true, maxRotation: 0, autoSkipPadding: 12 },
            },
        },
    };
}

// قيمة فوق كل عمود (عدد الأعمدة قليل، فالتسمية المباشرة مقروءة)
const _barValueLabels = {
    id: "barValueLabels",
    afterDatasetsDraw(chart, _args, pluginOpts) {
        if (!pluginOpts || !pluginOpts.enabled) return;
        const { ctx } = chart;
        const meta = chart.getDatasetMeta(0);
        ctx.save();
        ctx.fillStyle = pluginOpts.color;
        ctx.font = `600 12px ${getComputedStyle(document.body).fontFamily}`;
        ctx.textAlign = "center";
        ctx.textBaseline = "bottom";
        meta.data.forEach((bar, i) => {
            const v = chart.data.datasets[0].data[i];
            if (v === null || v === undefined) return;
            ctx.fillText(formatNumber(v), bar.x, bar.y - 6);
        });
        ctx.restore();
    },
};

// خط عمودي رفيع عند النقطة النشطة (crosshair)
const _crosshair = {
    id: "crosshair",
    afterDatasetsDraw(chart, _args, pluginOpts) {
        if (!pluginOpts || !pluginOpts.enabled) return;
        const active = chart.tooltip && chart.tooltip.getActiveElements();
        if (!active || !active.length) return;
        const x = active[0].element.x;
        const { top, bottom } = chart.chartArea;
        const { ctx } = chart;
        ctx.save();
        ctx.strokeStyle = pluginOpts.color;
        ctx.lineWidth = 1;
        ctx.beginPath();
        ctx.moveTo(x, top);
        ctx.lineTo(x, bottom);
        ctx.stroke();
        ctx.restore();
    },
};

function _register(canvasId, renderFn) {
    _chartRenderers[canvasId] = renderFn;
    renderFn();
}

function _destroyIfExists(canvasId) {
    if (_chartInstances[canvasId]) {
        _chartInstances[canvasId].destroy();
        delete _chartInstances[canvasId];
    }
}

function renderBarChart(canvasId, labels, values, opts = {}) {
    _register(canvasId, () => {
        const canvas = document.getElementById(canvasId);
        if (!canvas) return;
        const th = _theme();
        _destroyIfExists(canvasId);
        const options = _baseOptions(th, { ...opts, topPadding: 22 });
        options.plugins.barValueLabels = { enabled: labels.length <= 12, color: th.muted };
        options.scales.x.ticks.autoSkip = labels.length > 12;

        _chartInstances[canvasId] = new Chart(canvas, {
            type: "bar",
            data: {
                labels,
                datasets: [{
                    label: opts.label || "",
                    data: values,
                    backgroundColor: th.series,
                    hoverBackgroundColor: th.series,
                    borderRadius: 4,
                    borderSkipped: "start",
                    maxBarThickness: 24,
                    categoryPercentage: 0.6,
                }],
            },
            options,
            plugins: [_barValueLabels],
        });
    });
}

function renderLineChart(canvasId, labels, values, opts = {}) {
    _register(canvasId, () => {
        const canvas = document.getElementById(canvasId);
        if (!canvas) return;
        const th = _theme();
        _destroyIfExists(canvasId);
        const dense = labels.length > 24;
        const options = _baseOptions(th, opts);
        options.interaction = { mode: "index", intersect: false };
        options.plugins.crosshair = { enabled: true, color: th.axis };

        _chartInstances[canvasId] = new Chart(canvas, {
            type: "line",
            data: {
                labels,
                datasets: [{
                    label: opts.label || "",
                    data: values,
                    borderColor: th.series,
                    borderWidth: 2,
                    borderJoinStyle: "round",
                    borderCapStyle: "round",
                    backgroundColor: _withAlpha(th.series, 0.10),
                    fill: "origin",
                    tension: 0.25,
                    spanGaps: true,
                    pointRadius: dense ? 0 : 4,
                    pointHoverRadius: 6,
                    pointBackgroundColor: th.series,
                    pointBorderColor: th.surface,
                    pointBorderWidth: 2,
                    pointHoverBorderWidth: 2,
                    pointHitRadius: 12,
                }],
            },
            options,
            plugins: [_crosshair],
        });
    });
}

function renderDoughnutChart(canvasId, labels, values, opts = {}) {
    _register(canvasId, () => {
        const canvas = document.getElementById(canvasId);
        if (!canvas) return;
        const th = _theme();
        _destroyIfExists(canvasId);
        _chartInstances[canvasId] = new Chart(canvas, {
            type: "doughnut",
            data: {
                labels,
                datasets: [{ data: values, backgroundColor: opts.colors || [th.series], borderColor: th.surface, borderWidth: 2 }],
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { position: "bottom", rtl: IS_RTL, labels: { color: th.muted } } },
            },
        });
    });
}

// عند تبديل الوضع الداكن/الفاتح: إعادة رسم كل الرسوم بألوان الوضع الجديد
document.addEventListener("themechange", () => {
    Object.values(_chartRenderers).forEach((fn) => fn());
});
