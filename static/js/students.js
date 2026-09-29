/* ===================== منطق صفحات الطلاب ===================== */

/* ---------- صفحة قائمة الطلاب ---------- */
async function loadStudentsList(search = "") {
    const body = document.getElementById("students-body");
    if (!body) return;
    body.innerHTML = `<tr><td colspan="7"><div class="spinner"></div></td></tr>`;

    try {
        const query = search ? `?search=${encodeURIComponent(search)}` : "";
        const students = await api.get(`/students${query}`);

        if (students.length === 0) {
            body.innerHTML = `<tr><td colspan="7">
                <div class="empty-state">
                    <div class="icon-wrap">${icon("users", "icon-lg")}</div>
                    <h4>${t("no_students")}</h4>
                    <p>${t("no_students_hint")}</p>
                    <div class="flex-center gap-8">
                        <button class="btn btn-primary" onclick="openStudentModal()">${icon("plus", "icon-sm")} ${t("add_student")}</button>
                        <button class="btn btn-outline" onclick="openImportModal()">${icon("upload", "icon-sm")} ${t("import_excel")}</button>
                    </div>
                </div>
            </td></tr>`;
            return;
        }

        body.innerHTML = students.map((s) => `
            <tr>
                <td>
                    <a href="/students/${s.id}" class="name-cell">
                        <span class="avatar">${initials(s.name)}</span>
                        <span class="link-strong">${escapeHtml(s.name)}</span>
                    </a>
                </td>
                <td class="text-muted">${escapeHtml(s.class || "—")}</td>
                <td class="text-muted">${escapeHtml(s.section || "—")}</td>
                <td>${gradeCell(s.average)}</td>
                <td class="num">${s.grades_count}</td>
                <td class="num text-muted">${formatDate(s.created_at)}</td>
                <td>
                    <div class="table-actions">
                        <a class="btn btn-icon btn-outline" href="/students/${s.id}" title="${t("view")}" aria-label="${t("view")}">${icon("eye")}</a>
                        <button class="btn btn-icon btn-outline" title="${t("edit")}" aria-label="${t("edit")}" onclick='openStudentModal(${JSON.stringify(s)})'>${icon("edit")}</button>
                        <button class="btn btn-icon btn-danger" title="${t("delete")}" aria-label="${t("delete")}" onclick="deleteStudent(${s.id}, '${escapeHtml(s.name).replace(/'/g, "\\'")}')">${icon("trash")}</button>
                    </div>
                </td>
            </tr>`).join("");
    } catch (e) {
        body.innerHTML = `<tr><td colspan="7" class="text-center text-muted">${t("load_students_failed")}</td></tr>`;
    }
}

function openStudentModal(student = null) {
    const form = document.getElementById("student-form");
    form.reset();
    document.getElementById("student-id").value = "";
    if (student) {
        document.getElementById("student-modal-title").textContent = t("modal_edit_student");
        document.getElementById("student-id").value = student.id;
        document.getElementById("student-name").value = student.name || "";
        document.getElementById("student-class").value = student.class || "";
        document.getElementById("student-section").value = student.section || "";
        document.getElementById("student-notes").value = student.notes || "";
    } else {
        document.getElementById("student-modal-title").textContent = t("modal_add_student");
    }
    openModal("student-modal");
    setTimeout(() => document.getElementById("student-name").focus(), 50);
}

async function saveStudent() {
    const name = document.getElementById("student-name").value.trim();
    if (!name) { showToast(t("err_student_name_required"), "error"); return; }

    const payload = {
        name,
        class: document.getElementById("student-class").value.trim(),
        section: document.getElementById("student-section").value.trim(),
        notes: document.getElementById("student-notes").value.trim(),
    };
    const id = document.getElementById("student-id").value;

    try {
        if (id) {
            await api.put(`/students/${id}`, payload);
            showToast(t("student_updated"));
        } else {
            await api.post("/students", payload);
            showToast(t("student_added"));
        }
        closeModal("student-modal");
        if (document.getElementById("students-body")) {
            loadStudentsList(document.getElementById("student-search")?.value.trim() || "");
        }
        if (window.STUDENT_ID) loadStudentDetails();
    } catch (e) { /* تم عرض رسالة الخطأ بالفعل */ }
}

async function deleteStudent(id, name) {
    const confirmed = await showConfirm({
        title: t("delete_student_title"),
        message: t("delete_student_msg", { name }),
    });
    if (!confirmed) return;

    try {
        await api.delete(`/students/${id}`);
        showToast(t("student_deleted"));
        loadStudentsList(document.getElementById("student-search")?.value.trim() || "");
    } catch (e) {}
}

/* ---------- استيراد الطلاب من Excel ---------- */
function openImportModal() {
    document.getElementById("import-file").value = "";
    document.getElementById("import-file-name").textContent = t("no_file_chosen");
    document.getElementById("import-result").innerHTML = "";
    openModal("import-modal");
}

async function runImport() {
    const input = document.getElementById("import-file");
    const file = input.files[0];
    if (!file) { showToast(t("import_no_file"), "error"); return; }

    const form = new FormData();
    form.append("file", file);
    form.append("skip_duplicates", document.getElementById("import-skip-duplicates").checked ? "1" : "0");

    const btn = document.getElementById("btn-run-import");
    btn.disabled = true;
    try {
        const result = await api.upload("/students/import", form);
        showToast(result.message);
        const resultBox = document.getElementById("import-result");
        resultBox.innerHTML = `
            <div class="import-summary">
                ${icon("check-circle")} <span>${escapeHtml(result.message)}</span>
            </div>
            ${result.skipped_names.length ? `
            <details class="import-skipped">
                <summary>${t("import_skipped_rows")} (${result.skipped})</summary>
                <ul>${result.skipped_names.map(s => `<li>${escapeHtml(s.name)} <span class="text-faint">— ${escapeHtml(s.reason)}</span></li>`).join("")}</ul>
            </details>` : ""}`;
        loadStudentsList(document.getElementById("student-search")?.value.trim() || "");
    } catch (e) {
        /* تم عرض رسالة الخطأ */
    } finally {
        btn.disabled = false;
    }
}

function initStudentsPage() {
    document.getElementById("btn-add-student").addEventListener("click", () => openStudentModal());
    document.getElementById("btn-import-students").addEventListener("click", openImportModal);
    document.getElementById("btn-run-import").addEventListener("click", runImport);
    document.getElementById("import-file").addEventListener("change", (e) => {
        const file = e.target.files[0];
        document.getElementById("import-file-name").textContent = file ? file.name : t("no_file_chosen");
        document.getElementById("import-result").innerHTML = "";
    });
    document.getElementById("student-search").addEventListener("input", debounce((e) => {
        loadStudentsList(e.target.value.trim());
    }, 300));
    loadStudentsList();
}

/* ---------- صفحة تفاصيل الطالب ---------- */
async function loadStudentDetails() {
    const container = document.getElementById("student-content");
    try {
        const data = await api.get(`/students/${window.STUDENT_ID}`);
        renderStudentDetails(data, container);
    } catch (e) {
        container.innerHTML = `<div class="empty-state"><div class="icon-wrap">${icon("alert-triangle", "icon-lg")}</div><h4>${t("load_student_failed")}</h4></div>`;
    }
}

function renderStudentDetails(data, container) {
    const { student, subjects, overall } = data;
    document.getElementById("breadcrumb-name").textContent = student.name;
    document.title = `${student.name} - ${t("app_title")}`;

    const subjectsWithExams = subjects.filter(s => s.exams.length > 0);

    container.innerHTML = `
        <div class="panel">
            <div class="profile-header">
                <div class="profile-avatar">${initials(student.name)}</div>
                <div>
                    <h2>${escapeHtml(student.name)}</h2>
                    <div class="profile-meta">
                        <span class="flex gap-8">${icon("layers", "icon-sm")} ${escapeHtml(student.class || "—")}</span>
                        <span class="flex gap-8">${icon("tag", "icon-sm")} ${escapeHtml(student.section || "—")}</span>
                        <span class="flex gap-8">${icon("calendar", "icon-sm")} ${t("joined_on", { date: formatDate(student.created_at) })}</span>
                    </div>
                    ${student.notes ? `<p class="text-muted mt-8 flex gap-8">${icon("note", "icon-sm")} ${escapeHtml(student.notes)}</p>` : ""}
                </div>
                <div class="flex gap-8" style="margin-inline-start:auto">
                    <button class="btn btn-outline btn-sm" onclick='openStudentModal(${JSON.stringify(student)})'>${icon("edit", "icon-sm")} ${t("edit")}</button>
                </div>
            </div>
        </div>

        <div class="cards-grid">
            <div class="stat-card"><div class="stat-icon blue">${icon("trending-up", "icon-md")}</div><div><div class="stat-value num">${formatNumber(overall.average)}</div><div class="stat-label">${t("overall_avg")}</div></div></div>
            <div class="stat-card"><div class="stat-icon">${icon("arrow-up", "icon-md")}</div><div><div class="stat-value num">${formatNumber(overall.highest)}</div><div class="stat-label">${t("highest_grade")}</div></div></div>
            <div class="stat-card"><div class="stat-icon">${icon("arrow-down", "icon-md")}</div><div><div class="stat-value num">${formatNumber(overall.lowest)}</div><div class="stat-label">${t("lowest_grade")}</div></div></div>
            <div class="stat-card"><div class="stat-icon">${icon("clipboard", "icon-md")}</div><div><div class="stat-value num">${overall.exam_count}</div><div class="stat-label">${t("exams_count")}</div></div></div>
            <div class="stat-card"><div class="stat-icon">${icon("book", "icon-md")}</div><div><div class="stat-value num">${overall.subject_count}</div><div class="stat-label">${t("subjects_count")}</div></div></div>
        </div>

        ${subjectsWithExams.length ? `
        <div class="panel">
            <div class="panel-header">
                <h3 class="flex gap-8">${icon("trending-up")} ${t("progress_title")}</h3>
                <select class="form-control" id="subject-chart-select" style="width:220px" aria-label="${t("col_subject")}">
                    ${subjectsWithExams.map(s => `<option value="${s.subject_id}">${escapeHtml(s.subject_name)}</option>`).join("")}
                </select>
            </div>
            <div class="chart-wrap">
                <canvas id="student-progress-chart"></canvas>
            </div>
        </div>` : ""}

        ${subjectsWithExams.length === 0 ? `
        <div class="empty-state">
            <div class="icon-wrap">${icon("inbox", "icon-lg")}</div>
            <h4>${t("no_exams_for_student")}</h4>
            <p>${t("no_exams_for_student_hint")}</p>
        </div>` : subjectsWithExams.map(s => `
        <div class="panel">
            <div class="panel-header">
                <h3 class="flex gap-8">${icon("book")} ${escapeHtml(s.subject_name)}</h3>
                <span class="flex gap-8 text-muted">${t("avg_label")} ${gradeCell(s.average)}</span>
            </div>
            <div class="table-wrap">
                <table>
                    <thead><tr><th>${t("col_exam")}</th><th>${t("col_grade")}</th></tr></thead>
                    <tbody>
                        ${s.exams.map(ex => `
                            <tr>
                                <td><a class="link-strong" href="/exams/${ex.exam_id}">${escapeHtml(ex.exam_name)}</a></td>
                                <td>${gradeCell(ex.grade, t("no_grade"))}</td>
                            </tr>`).join("")}
                    </tbody>
                </table>
            </div>
        </div>`).join("")}
    `;

    if (subjectsWithExams.length) {
        const select = document.getElementById("subject-chart-select");
        const renderChart = () => {
            const subj = subjectsWithExams.find(s => String(s.subject_id) === select.value);
            const labels = subj.exams.map(e => e.exam_name);
            const values = subj.exams.map(e => e.grade);
            renderLineChart("student-progress-chart", labels, values, { label: subj.subject_name, max: 100 });
        };
        select.addEventListener("change", renderChart);
        renderChart();
    }
}

document.addEventListener("DOMContentLoaded", () => {
    const saveBtn = document.getElementById("btn-save-student");
    if (saveBtn) saveBtn.addEventListener("click", saveStudent);
    if (document.getElementById("students-body")) initStudentsPage();
    if (document.getElementById("student-content")) loadStudentDetails();
});
