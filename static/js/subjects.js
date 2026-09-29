/* ===================== منطق صفحات المواد ===================== */

/* ---------- صفحة قائمة المواد ---------- */
async function loadSubjectsList(search = "") {
    const body = document.getElementById("subjects-body");
    if (!body) return;
    body.innerHTML = `<tr><td colspan="5"><div class="spinner"></div></td></tr>`;

    try {
        const query = search ? `?search=${encodeURIComponent(search)}` : "";
        const subjects = await api.get(`/subjects${query}`);

        if (subjects.length === 0) {
            body.innerHTML = `<tr><td colspan="5">
                <div class="empty-state">
                    <div class="icon-wrap">${icon("book", "icon-lg")}</div>
                    <h4>${t("no_subjects")}</h4>
                    <p>${t("no_subjects_hint")}</p>
                    <button class="btn btn-primary" onclick="openSubjectModal()">${icon("plus", "icon-sm")} ${t("add_subject")}</button>
                </div>
            </td></tr>`;
            return;
        }

        body.innerHTML = subjects.map((s) => `
            <tr>
                <td><a href="/subjects/${s.id}" class="link-strong flex gap-8">${icon("book", "icon-sm")} ${escapeHtml(s.name)}</a></td>
                <td class="num">${s.exams_count}</td>
                <td class="num">${s.grades_count}</td>
                <td>${gradeCell(s.average)}</td>
                <td>
                    <div class="table-actions">
                        <a class="btn btn-icon btn-outline" href="/subjects/${s.id}" title="${t("open")}" aria-label="${t("open")}">${icon("eye")}</a>
                        <button class="btn btn-icon btn-outline" title="${t("edit")}" aria-label="${t("edit")}" onclick='openSubjectModal(${JSON.stringify(s)})'>${icon("edit")}</button>
                        <button class="btn btn-icon btn-danger" title="${t("delete")}" aria-label="${t("delete")}" onclick="deleteSubject(${s.id}, '${escapeHtml(s.name).replace(/'/g, "\\'")}')">${icon("trash")}</button>
                    </div>
                </td>
            </tr>`).join("");
    } catch (e) {
        body.innerHTML = `<tr><td colspan="5" class="text-center text-muted">${t("load_subjects_failed")}</td></tr>`;
    }
}

function openSubjectModal(subject = null) {
    const form = document.getElementById("subject-form");
    form.reset();
    document.getElementById("subject-id").value = "";
    if (subject) {
        document.getElementById("subject-modal-title").textContent = t("modal_edit_subject");
        document.getElementById("subject-id").value = subject.id;
        document.getElementById("subject-name").value = subject.name || "";
    } else {
        document.getElementById("subject-modal-title").textContent = t("modal_add_subject");
    }
    openModal("subject-modal");
    setTimeout(() => document.getElementById("subject-name").focus(), 50);
}

async function saveSubject() {
    const name = document.getElementById("subject-name").value.trim();
    if (!name) { showToast(t("err_subject_name_required"), "error"); return; }
    const id = document.getElementById("subject-id").value;

    try {
        if (id) {
            await api.put(`/subjects/${id}`, { name });
            showToast(t("subject_updated"));
        } else {
            await api.post("/subjects", { name });
            showToast(t("subject_added"));
        }
        closeModal("subject-modal");
        if (document.getElementById("subjects-body")) {
            loadSubjectsList(document.getElementById("subject-search")?.value.trim() || "");
        }
        if (window.SUBJECT_ID) loadSubjectDetails();
    } catch (e) {}
}

async function deleteSubject(id, name) {
    const confirmed = await showConfirm({
        title: t("delete_subject_title"),
        message: t("delete_subject_msg", { name }),
    });
    if (!confirmed) return;

    try {
        await api.delete(`/subjects/${id}`);
        showToast(t("subject_deleted"));
        if (window.location.pathname.startsWith(`/subjects/${id}`)) {
            window.location.href = "/subjects";
        } else {
            loadSubjectsList(document.getElementById("subject-search")?.value.trim() || "");
        }
    } catch (e) {}
}

function initSubjectsPage() {
    document.getElementById("btn-add-subject").addEventListener("click", () => openSubjectModal());
    document.getElementById("subject-search").addEventListener("input", debounce((e) => {
        loadSubjectsList(e.target.value.trim());
    }, 300));
    loadSubjectsList();
}

/* ---------- صفحة تفاصيل المادة ---------- */
async function loadSubjectDetails() {
    const container = document.getElementById("subject-content");
    if (!container) return;
    try {
        const data = await api.get(`/subjects/${window.SUBJECT_ID}`);
        renderSubjectDetails(data, container);
    } catch (e) {
        container.innerHTML = `<div class="empty-state"><div class="icon-wrap">${icon("alert-triangle", "icon-lg")}</div><h4>${t("load_subject_failed")}</h4></div>`;
    }
}
window.refreshSubjectDetails = loadSubjectDetails;

function renderSubjectDetails(data, container) {
    const { subject, exams, stats } = data;
    document.getElementById("breadcrumb-name").textContent = subject.name;
    document.title = `${subject.name} - ${t("app_title")}`;

    const studentStat = (s) => s
        ? `<div class="stat-value" style="font-size:16px">${escapeHtml(s.name)}</div><div class="stat-label">%LABEL% · <span class="num">${formatNumber(s.average)}</span></div>`
        : `<div class="stat-value">—</div><div class="stat-label">%LABEL%</div>`;

    container.innerHTML = `
        <div class="panel">
            <div class="flex-between">
                <div>
                    <h2 class="flex gap-8">${icon("book")} ${escapeHtml(subject.name)}</h2>
                    <p class="text-muted mt-8">${t("added_on", { date: formatDate(subject.created_at) })}</p>
                </div>
                <div class="flex gap-8">
                    <button class="btn btn-outline btn-sm" onclick='openSubjectModal(${JSON.stringify(subject)})'>${icon("edit", "icon-sm")} ${t("edit")}</button>
                    <button class="btn btn-danger btn-sm" onclick="deleteSubject(${subject.id}, '${escapeHtml(subject.name).replace(/'/g, "\\'")}')">${icon("trash", "icon-sm")} ${t("delete")}</button>
                </div>
            </div>
        </div>

        <div class="cards-grid">
            <div class="stat-card"><div class="stat-icon">${icon("clipboard", "icon-md")}</div><div><div class="stat-value num">${stats.exams_count}</div><div class="stat-label">${t("exams_count")}</div></div></div>
            <div class="stat-card"><div class="stat-icon blue">${icon("trending-up", "icon-md")}</div><div><div class="stat-value num">${formatNumber(stats.students_average)}</div><div class="stat-label">${t("students_avg_in_subject")}</div></div></div>
            <div class="stat-card"><div class="stat-icon">${icon("award", "icon-md")}</div><div>${studentStat(stats.best_student).replace("%LABEL%", t("best_student"))}</div></div>
            <div class="stat-card"><div class="stat-icon">${icon("trending-down", "icon-md")}</div><div>${studentStat(stats.worst_student).replace("%LABEL%", t("worst_student"))}</div></div>
        </div>

        <div class="panel">
            <div class="panel-header">
                <h3 class="flex gap-8">${icon("clipboard")} ${t("exams_heading", { n: exams.length })}</h3>
                <button class="btn btn-primary" onclick="openExamModal()">${icon("plus", "icon-sm")} ${t("add_exam")}</button>
            </div>
            <div id="exams-list-wrap">
                ${exams.length === 0 ? `
                <div class="empty-state">
                    <div class="icon-wrap">${icon("inbox", "icon-lg")}</div>
                    <h4>${t("no_exams_in_subject")}</h4>
                    <p>${t("no_exams_in_subject_hint")}</p>
                </div>` : `
                <div class="table-wrap">
                    <table>
                        <thead><tr><th>${t("col_exam_name")}</th><th>${t("col_grades_count")}</th><th>${t("average")}</th><th>${t("col_created")}</th><th></th></tr></thead>
                        <tbody>
                            ${exams.map(ex => `
                                <tr>
                                    <td><a href="/exams/${ex.id}" class="link-strong">${escapeHtml(ex.name)}</a></td>
                                    <td class="num">${ex.grades_count}</td>
                                    <td>${gradeCell(ex.average)}</td>
                                    <td class="num text-muted">${formatDate(ex.created_at)}</td>
                                    <td>
                                        <div class="table-actions">
                                            <a class="btn btn-icon btn-outline" href="/exams/${ex.id}" title="${t("manage_grades")}" aria-label="${t("manage_grades")}">${icon("checklist")}</a>
                                            <button class="btn btn-icon btn-outline" title="${t("edit_name")}" aria-label="${t("edit_name")}" onclick='openExamModal(${JSON.stringify(ex)})'>${icon("edit")}</button>
                                            <button class="btn btn-icon btn-danger" title="${t("delete")}" aria-label="${t("delete")}" onclick="deleteExam(${ex.id}, '${escapeHtml(ex.name).replace(/'/g, "\\'")}')">${icon("trash")}</button>
                                        </div>
                                    </td>
                                </tr>`).join("")}
                        </tbody>
                    </table>
                </div>`}
            </div>
        </div>
    `;
}

document.addEventListener("DOMContentLoaded", () => {
    const saveBtn = document.getElementById("btn-save-subject");
    if (saveBtn) saveBtn.addEventListener("click", saveSubject);
    if (document.getElementById("subjects-body")) initSubjectsPage();
    if (window.SUBJECT_ID && document.getElementById("subject-content")) loadSubjectDetails();
});
