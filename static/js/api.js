/* ===================== طبقة الاتصال بالـ API + أدوات مشتركة ===================== */
const API_BASE = "/api";
const LANG = window.LANG || "ar";
const IS_RTL = document.documentElement.dir === "rtl";

// الترجمة: النصوص تأتي من الخادم في window.I18N حسب اللغة المختارة
function t(key, params = {}) {
    const text = (window.I18N && window.I18N[key]) || key;
    return text.replace(/\{(\w+)\}/g, (_, k) => (params[k] !== undefined ? params[k] : `{${k}}`));
}

async function apiRequest(method, path, body) {
    const options = {
        method,
        headers: { "Content-Type": "application/json" },
    };
    if (body !== undefined) options.body = JSON.stringify(body);

    let response;
    try {
        response = await fetch(API_BASE + path, options);
    } catch (err) {
        showToast(t("server_unreachable"), "error");
        throw err;
    }

    let data = null;
    const text = await response.text();
    if (text) {
        try { data = JSON.parse(text); } catch (e) { data = null; }
    }

    if (!response.ok) {
        const message = (data && data.error) ? data.error : t("error_status", { n: response.status });
        showToast(message, "error");
        const err = new Error(message);
        err.data = data;
        throw err;
    }
    return data;
}

// رفع ملف (multipart) — يستخدم لاستيراد Excel
async function apiUpload(path, formData) {
    let response;
    try {
        response = await fetch(API_BASE + path, { method: "POST", body: formData });
    } catch (err) {
        showToast(t("server_unreachable"), "error");
        throw err;
    }
    let data = null;
    try { data = await response.json(); } catch (e) { data = null; }
    if (!response.ok) {
        const message = (data && data.error) ? data.error : t("error_status", { n: response.status });
        showToast(message, "error");
        throw new Error(message);
    }
    return data;
}

const api = {
    get: (path) => apiRequest("GET", path),
    post: (path, body) => apiRequest("POST", path, body),
    put: (path, body) => apiRequest("PUT", path, body),
    delete: (path) => apiRequest("DELETE", path),
    upload: apiUpload,
};

/* ===================== Toast Notifications ===================== */
function showToast(message, type = "success") {
    let container = document.querySelector(".toast-container");
    if (!container) {
        container = document.createElement("div");
        container.className = "toast-container";
        document.body.appendChild(container);
    }
    const iconNames = { success: "check-circle", error: "x-circle", warning: "alert-triangle" };
    const toast = document.createElement("div");
    toast.className = `toast ${type}`;
    toast.innerHTML = `<span class="toast-icon">${icon(iconNames[type] || "info-circle")}</span><span>${escapeHtml(message)}</span>`;
    container.appendChild(toast);
    setTimeout(() => {
        toast.style.opacity = "0";
        toast.style.transition = "opacity .25s ease";
        setTimeout(() => toast.remove(), 250);
    }, 3200);
}

/* ===================== Confirm Dialog ===================== */
function showConfirm({ title = t("confirm_delete_title"), message = t("confirm_default_msg"), confirmText = t("delete"), cancelText = t("cancel") } = {}) {
    return new Promise((resolve) => {
        let backdrop = document.getElementById("global-confirm-modal");
        if (backdrop) backdrop.remove();

        backdrop = document.createElement("div");
        backdrop.id = "global-confirm-modal";
        backdrop.className = "modal-backdrop open";
        backdrop.innerHTML = `
            <div class="modal confirm-modal">
                <div class="modal-body">
                    <div class="confirm-icon">${icon("alert-triangle", "icon-md")}</div>
                    <h3 class="mb-16">${escapeHtml(title)}</h3>
                    <p>${escapeHtml(message)}</p>
                </div>
                <div class="modal-footer flex-center">
                    <button class="btn btn-outline" data-action="cancel">${escapeHtml(cancelText)}</button>
                    <button class="btn btn-danger" data-action="confirm">${escapeHtml(confirmText)}</button>
                </div>
            </div>`;
        document.body.appendChild(backdrop);

        const cleanup = (result) => {
            backdrop.remove();
            resolve(result);
        };
        backdrop.querySelector('[data-action="cancel"]').onclick = () => cleanup(false);
        backdrop.querySelector('[data-action="confirm"]').onclick = () => cleanup(true);
        backdrop.addEventListener("click", (e) => { if (e.target === backdrop) cleanup(false); });
    });
}

/* ===================== Modals ===================== */
function openModal(id) {
    const modal = document.getElementById(id);
    if (modal) modal.classList.add("open");
}
function closeModal(id) {
    const modal = document.getElementById(id);
    if (modal) modal.classList.remove("open");
}
document.addEventListener("click", (e) => {
    if (e.target.classList && e.target.classList.contains("modal-backdrop")) {
        e.target.classList.remove("open");
    }
    if (e.target.closest("[data-close-modal]")) {
        const id = e.target.closest("[data-close-modal]").getAttribute("data-close-modal");
        closeModal(id);
    }
});
document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") {
        document.querySelectorAll(".modal-backdrop.open").forEach((m) => m.classList.remove("open"));
    }
});

/* ===================== أدوات مساعدة ===================== */
function escapeHtml(str) {
    if (str === null || str === undefined) return "";
    return String(str)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#39;");
}

function formatNumber(num) {
    if (num === null || num === undefined) return "—";
    return Number.isInteger(num) ? String(num) : num.toFixed(2).replace(/\.00$/, "");
}

function formatDate(str) {
    if (!str) return "—";
    const parts = str.split(" ")[0];
    return parts;
}

function initials(name) {
    if (!name) return "?";
    const parts = name.trim().split(/\s+/);
    if (parts.length === 1) return parts[0].charAt(0);
    return parts[0].charAt(0) + parts[1].charAt(0);
}

function gradeTier(value) {
    if (value >= 85) return "tier-good";
    if (value < 60) return "tier-low";
    return "";
}

// الرقم بلون النص، والمقياس بجانبه يحمل المستوى — اللون لا يحمل المعنى وحده
function gradeCell(value, emptyText = "—") {
    if (value === null || value === undefined) return `<span class="grade-empty">${emptyText}</span>`;
    const pct = Math.max(0, Math.min(100, value));
    return `<span class="grade"><span class="grade-num">${formatNumber(value)}</span><span class="meter ${gradeTier(value)}"><span class="meter-fill" style="inline-size:${pct}%"></span></span></span>`;
}

function debounce(fn, delay = 300) {
    let timer;
    return (...args) => {
        clearTimeout(timer);
        timer = setTimeout(() => fn(...args), delay);
    };
}

/* ===================== الثيم (فاتح / داكن) ===================== */
function initTheme() {
    const current = document.documentElement.getAttribute("data-theme") || "light";
    updateThemeIcon(current);

    const btn = document.getElementById("theme-toggle");
    if (btn) {
        btn.addEventListener("click", () => {
            const now = document.documentElement.getAttribute("data-theme");
            const next = now === "dark" ? "light" : "dark";
            document.documentElement.setAttribute("data-theme", next);
            try { localStorage.setItem("theme", next); } catch (e) {}
            updateThemeIcon(next);
            document.dispatchEvent(new CustomEvent("themechange", { detail: next }));
        });
    }
}
function updateThemeIcon(theme) {
    const btn = document.getElementById("theme-toggle");
    if (btn) btn.innerHTML = icon(theme === "dark" ? "sun" : "moon");
}

/* ===================== قائمة الجوال (Sidebar) ===================== */
function initSidebar() {
    const toggle = document.getElementById("sidebar-toggle");
    const backdrop = document.querySelector(".sidebar-backdrop");
    if (toggle) {
        toggle.addEventListener("click", () => document.body.classList.toggle("sidebar-open"));
    }
    if (backdrop) {
        backdrop.addEventListener("click", () => document.body.classList.remove("sidebar-open"));
    }
}

/* ===================== البحث العام في الشريط العلوي ===================== */
function initGlobalSearch() {
    const input = document.getElementById("global-search-input");
    const results = document.getElementById("global-search-results");
    if (!input || !results) return;

    const runSearch = debounce(async (q) => {
        if (!q) { results.classList.remove("open"); results.innerHTML = ""; return; }
        try {
            const data = await api.get(`/search?q=${encodeURIComponent(q)}`);
            renderSearchResults(data, results);
        } catch (e) { /* تم عرض الخطأ بالفعل */ }
    }, 300);

    input.addEventListener("input", () => runSearch(input.value.trim()));
    input.addEventListener("focus", () => { if (input.value.trim()) results.classList.add("open"); });
    document.addEventListener("click", (e) => {
        if (!e.target.closest(".topbar-search")) results.classList.remove("open");
    });
}

function renderSearchResults(data, container) {
    const total = data.students.length + data.subjects.length + data.exams.length;
    if (total === 0) {
        container.innerHTML = `<div class="empty">${t("no_results")}</div>`;
        container.classList.add("open");
        return;
    }
    let html = "";
    if (data.students.length) {
        html += `<div class="group-title">${t("nav_students")}</div>`;
        data.students.forEach((s) => {
            html += `<a class="result-item" href="/students/${s.id}">
                <span class="flex gap-8">${icon("user", "icon-sm")} ${escapeHtml(s.name)}</span>
                <span class="text-muted">${escapeHtml(s.class || "")}</span>
            </a>`;
        });
    }
    if (data.subjects.length) {
        html += `<div class="group-title">${t("nav_subjects")}</div>`;
        data.subjects.forEach((s) => {
            html += `<a class="result-item" href="/subjects/${s.id}">
                <span class="flex gap-8">${icon("book", "icon-sm")} ${escapeHtml(s.name)}</span>
            </a>`;
        });
    }
    if (data.exams.length) {
        html += `<div class="group-title">${t("nav_exams")}</div>`;
        data.exams.forEach((e) => {
            html += `<a class="result-item" href="/exams/${e.id}">
                <span class="flex gap-8">${icon("clipboard", "icon-sm")} ${escapeHtml(e.name)}</span>
                <span class="text-muted">${escapeHtml(e.subject_name)}</span>
            </a>`;
        });
    }
    container.innerHTML = html;
    container.classList.add("open");
}

document.addEventListener("DOMContentLoaded", () => {
    initTheme();
    initSidebar();
    initGlobalSearch();
});
