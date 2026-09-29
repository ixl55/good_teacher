/* ===================== منطق صفحة إدارة درجات الامتحان ===================== */
const GRADE_MIN = 0;
const GRADE_MAX = 100;
let _dirtyGrades = {};

async function loadExamPage() {
    const container = document.getElementById("exam-content");
    try {
        const data = await api.get(`/exams/${window.EXAM_ID}`);
        renderExamPage(data);
    } catch (e) {
        container.innerHTML = `<div class="empty-state"><div class="icon-wrap">${icon("alert-triangle", "icon-lg")}</div><h4>${t("load_exam_failed")}</h4></div>`;
    }
}

// الحقل الفارغ مسموح (الطالب بدون درجة)؛ غير ذلك يجب أن يكون رقمًا صحيحًا من 0 إلى 100
function isValidGradeInput(value) {
    if (value.trim() === "") return true;
    const n = Number(value);
    return Number.isInteger(n) && n >= GRADE_MIN && n <= GRADE_MAX;
}

function validateGradeInput(input) {
    const ok = isValidGradeInput(input.value);
    input.classList.toggle("invalid", !ok);
    input.setAttribute("aria-invalid", ok ? "false" : "true");
    return ok;
}

function renderExamPage(data) {
    const { exam, students } = data;
    _dirtyGrades = {};

    document.title = `${exam.name} - ${t("app_title")}`;
    document.getElementById("exam-breadcrumb").innerHTML = `
        <a href="/subjects" class="flex gap-8">${icon("book", "icon-sm")} ${t("nav_subjects")}</a> <span>/</span>
        <a href="/subjects/${exam.subject_id}">${escapeHtml(exam.subject_name)}</a> <span>/</span>
        <span>${escapeHtml(exam.name)}</span>
    `;

    const container = document.getElementById("exam-content");
    container.innerHTML = `
        <div class="panel">
            <div class="flex-between">
                <div>
                    <h2 class="flex gap-8">${icon("clipboard")} ${escapeHtml(exam.name)}</h2>
                    <p class="text-muted mt-8">${t("label_subject")}: <a class="text-link" href="/subjects/${exam.subject_id}">${escapeHtml(exam.subject_name)}</a> · ${t("created_on", { date: formatDate(exam.created_at) })}</p>
                </div>
                <div class="flex gap-8">
                    <button class="btn btn-outline btn-sm" id="btn-edit-exam-name">${icon("edit", "icon-sm")} ${t("edit_name")}</button>
                    <button class="btn btn-danger btn-sm" id="btn-delete-exam">${icon("trash", "icon-sm")} ${t("delete_exam")}</button>
                </div>
            </div>
        </div>

        <div class="panel">
            <div class="panel-header">
                <div>
                    <h3 class="flex gap-8">${icon("checklist")} ${t("student_grades", { n: students.length })}</h3>
                    <p class="hint mt-8">${t("grade_range_hint")}</p>
                </div>
                <input type="text" id="exam-student-search" class="form-control exam-name-search" placeholder="${t("search_student")}">
            </div>

            ${students.length === 0 ? `
            <div class="empty-state">
                <div class="icon-wrap">${icon("users", "icon-lg")}</div>
                <h4>${t("no_students_system")}</h4>
                <p>${t("no_students_system_hint")}</p>
                <a class="btn btn-primary" href="/students">${icon("plus", "icon-sm")} ${t("add_student")}</a>
            </div>` : `
            <div class="table-wrap">
                <table>
                    <thead><tr><th>${t("col_student")}</th><th class="hide-on-phone">${t("col_class")}</th><th>${t("col_grade")}</th></tr></thead>
                    <tbody id="exam-grades-body">
                        ${students.map(s => `
                            <tr data-student-row data-name="${escapeHtml(s.student_name).toLowerCase()}">
                                <td><span class="name-cell"><span class="avatar">${initials(s.student_name)}</span> ${escapeHtml(s.student_name)}</span></td>
                                <td class="text-muted hide-on-phone">${escapeHtml(s.class || "—")}</td>
                                <td>
                                    <div class="grade-stepper">
                                        <button type="button" class="step-btn" data-step="-1" tabindex="-1" aria-label="${t("grade_decrease")}">${icon("minus", "icon-sm")}</button>
                                        <input type="number" inputmode="numeric" step="1" min="${GRADE_MIN}" max="${GRADE_MAX}"
                                            class="grade-input" data-student-id="${s.student_id}"
                                            aria-label="${t("col_grade")} — ${escapeHtml(s.student_name)}"
                                            value="${s.grade !== null ? s.grade : ""}" placeholder="—">
                                        <button type="button" class="step-btn" data-step="1" tabindex="-1" aria-label="${t("grade_increase")}">${icon("plus", "icon-sm")}</button>
                                    </div>
                                </td>
                            </tr>`).join("")}
                    </tbody>
                </table>
            </div>
            <div class="flex-between sticky-actions">
                <span class="text-muted" id="dirty-indicator" aria-live="polite"></span>
                <button class="btn btn-primary" id="btn-save-all-grades">${icon("save", "icon-sm")} ${t("save_all_grades")}</button>
            </div>`}
        </div>
    `;

    if (students.length) {
        const inputs = Array.from(document.querySelectorAll(".grade-input"));
        inputs.forEach((input, i) => {
            input.addEventListener("input", () => {
                input.classList.add("dirty");
                _dirtyGrades[input.dataset.studentId] = input.value;
                validateGradeInput(input);
                updateDirtyIndicator();
            });
            // Enter ينقل إلى الطالب التالي لتسريع الإدخال؛ الأسهم تزيد/تنقص بمقدار 1
            input.addEventListener("keydown", (e) => {
                if (e.key === "ArrowUp" || e.key === "ArrowDown") {
                    e.preventDefault();
                    stepGrade(input, e.key === "ArrowUp" ? 1 : -1);
                } else if (e.key === "Enter") {
                    e.preventDefault();
                    const next = inputs.slice(i + 1).find(el => el.closest("tr").style.display !== "none");
                    if (next) { next.focus(); next.select(); } else { saveAllGrades(); }
                }
            });
        });
        document.querySelectorAll(".step-btn").forEach(bindStepButton);
        document.getElementById("btn-save-all-grades").addEventListener("click", saveAllGrades);
        document.getElementById("exam-student-search").addEventListener("input", (e) => {
            const q = e.target.value.trim().toLowerCase();
            document.querySelectorAll("[data-student-row]").forEach((row) => {
                row.style.display = row.dataset.name.includes(q) ? "" : "none";
            });
        });
    }

    document.getElementById("btn-edit-exam-name").addEventListener("click", () => {
        document.getElementById("exam-edit-name").value = exam.name;
        openModal("exam-edit-modal");
    });
    document.getElementById("btn-delete-exam").addEventListener("click", async () => {
        const confirmed = await showConfirm({
            title: t("delete_exam_title"),
            message: t("delete_exam_msg", { name: exam.name }),
        });
        if (!confirmed) return;
        try {
            await api.delete(`/exams/${exam.id}`);
            _dirtyGrades = {};
            showToast(t("exam_deleted"));
            window.location.href = `/subjects/${exam.subject_id}`;
        } catch (e) {}
    });
}

// زيادة/إنقاص الدرجة بمقدار 1. الحقل الفارغ يبدأ من 0، والقيمة تبقى بين 0 و 100
function stepGrade(input, delta) {
    const current = input.value.trim();
    let next;
    if (current === "" || !Number.isFinite(Number(current))) {
        next = GRADE_MIN;
    } else {
        next = Math.min(GRADE_MAX, Math.max(GRADE_MIN, Math.round(Number(current)) + delta));
    }
    if (String(next) === current) return;
    input.value = next;
    input.dispatchEvent(new Event("input", { bubbles: true }));
}

// الضغط المطوّل يكرر الزيادة/الإنقاص
function bindStepButton(btn) {
    const input = btn.parentElement.querySelector(".grade-input");
    const delta = Number(btn.dataset.step);
    let delayTimer = null;
    let repeatTimer = null;
    const stop = () => {
        clearTimeout(delayTimer);
        clearInterval(repeatTimer);
    };
    btn.addEventListener("pointerdown", (e) => {
        e.preventDefault();
        stepGrade(input, delta);
        delayTimer = setTimeout(() => {
            repeatTimer = setInterval(() => stepGrade(input, delta), 70);
        }, 400);
    });
    ["pointerup", "pointerleave", "pointercancel"].forEach((ev) => btn.addEventListener(ev, stop));
    // تفعيل الزر من لوحة المفاتيح أيضًا
    btn.addEventListener("keydown", (e) => {
        if (e.key === "Enter" || e.key === " ") { e.preventDefault(); stepGrade(input, delta); }
    });
}

function updateDirtyIndicator() {
    const count = Object.keys(_dirtyGrades).length;
    const el = document.getElementById("dirty-indicator");
    if (el) el.textContent = count > 0 ? t("unsaved_n", { n: count }) : "";
}

async function saveAllGrades() {
    const inputs = Array.from(document.querySelectorAll(".grade-input"));
    const invalid = inputs.filter((input) => !validateGradeInput(input));
    if (invalid.length) {
        showToast(t("invalid_grades_n", { n: invalid.length }), "error");
        const first = invalid[0];
        first.closest("tr").style.display = "";
        first.focus();
        return;
    }

    const grades = inputs.map((input) => ({
        student_id: parseInt(input.dataset.studentId, 10),
        grade: input.value.trim() === "" ? null : Number(input.value),
    }));

    try {
        await api.post(`/exams/${window.EXAM_ID}/grades`, { grades });
        showToast(t("grades_saved"));
        _dirtyGrades = {};
        inputs.forEach((i) => i.classList.remove("dirty"));
        updateDirtyIndicator();
    } catch (e) {
        // الخادم يرجع الطلاب ذوي الدرجات غير الصالحة — نعلّمهم
        const ids = (e.data && e.data.invalid_student_ids) || [];
        ids.forEach((id) => {
            const input = document.querySelector(`.grade-input[data-student-id="${id}"]`);
            if (input) input.classList.add("invalid");
        });
    }
}

async function saveExamNameEdit() {
    const name = document.getElementById("exam-edit-name").value.trim();
    if (!name) { showToast(t("err_exam_name_required"), "error"); return; }
    try {
        await api.put(`/exams/${window.EXAM_ID}`, { name });
        showToast(t("exam_name_updated"));
        closeModal("exam-edit-modal");
        loadExamPage();
    } catch (e) {}
}

document.addEventListener("DOMContentLoaded", () => {
    if (document.getElementById("exam-content")) {
        loadExamPage();
        const saveNameBtn = document.getElementById("btn-save-exam-name");
        if (saveNameBtn) saveNameBtn.addEventListener("click", saveExamNameEdit);
    }
});

window.addEventListener("beforeunload", (e) => {
    if (Object.keys(_dirtyGrades).length > 0 && document.getElementById("exam-content")) {
        e.preventDefault();
        e.returnValue = "";
    }
});
