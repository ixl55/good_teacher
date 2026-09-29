/* ===================== منطق إدارة الامتحانات داخل صفحة المادة ===================== */

function openExamModal(exam = null) {
    const form = document.getElementById("exam-form");
    form.reset();
    document.getElementById("exam-id").value = "";
    if (exam) {
        document.getElementById("exam-modal-title").textContent = t("modal_edit_exam");
        document.getElementById("exam-id").value = exam.id;
        document.getElementById("exam-name").value = exam.name || "";
    } else {
        document.getElementById("exam-modal-title").textContent = t("modal_add_exam");
    }
    openModal("exam-modal");
    setTimeout(() => document.getElementById("exam-name").focus(), 50);
}

async function saveExam() {
    const name = document.getElementById("exam-name").value.trim();
    if (!name) { showToast(t("err_exam_name_required"), "error"); return; }
    const id = document.getElementById("exam-id").value;

    try {
        if (id) {
            await api.put(`/exams/${id}`, { name });
            showToast(t("exam_updated"));
            closeModal("exam-modal");
            if (window.refreshSubjectDetails) window.refreshSubjectDetails();
        } else {
            const exam = await api.post("/exams", { name, subject_id: window.SUBJECT_ID });
            showToast(t("exam_added"));
            // الانتقال مباشرة إلى صفحة إدخال الدرجات
            window.location.href = `/exams/${exam.id}`;
        }
    } catch (e) {}
}

async function deleteExam(id, name) {
    const confirmed = await showConfirm({
        title: t("delete_exam_title"),
        message: t("delete_exam_msg", { name }),
    });
    if (!confirmed) return;

    try {
        await api.delete(`/exams/${id}`);
        showToast(t("exam_deleted"));
        if (window.refreshSubjectDetails) window.refreshSubjectDetails();
    } catch (e) {}
}

document.addEventListener("DOMContentLoaded", () => {
    const saveBtn = document.getElementById("btn-save-exam");
    if (saveBtn) saveBtn.addEventListener("click", saveExam);
});
