"""API إدارة الطلاب + استيراد الطلاب من Excel."""
import io
import re

from flask import Blueprint, request, jsonify, send_file
from database import get_db, dict_from_row
from i18n import t, get_lang

students_bp = Blueprint("students", __name__, url_prefix="/api/students")

MAX_IMPORT_ROWS = 5000

# عناوين الأعمدة المقبولة عند الاستيراد (بعد التوحيد: أحرف صغيرة وبدون مسافات زائدة)
HEADER_ALIASES = {
    "name": {"name", "student", "student name", "full name", "الاسم", "اسم الطالب", "الاسم الكامل", "الطالب"},
    "class": {"class", "grade", "group", "class / group", "الصف", "المرحلة", "المجموعة", "الصف / المجموعة"},
    "section": {"section", "division", "الشعبة", "القسم", "الشعبة / القسم"},
    "notes": {"notes", "note", "ملاحظات", "ملاحظة"},
}


def _clean(value):
    if value is None:
        return None
    if isinstance(value, float) and value.is_integer():
        value = int(value)
    text = re.sub(r"\s+", " ", str(value)).strip()
    return text or None


def _student_fields(data):
    return (
        (data.get("class") or "").strip() or None,
        (data.get("section") or "").strip() or None,
        (data.get("notes") or "").strip() or None,
    )


@students_bp.route("", methods=["GET"])
def list_students():
    db = get_db()
    search = request.args.get("search", "").strip()
    query = """
        SELECT s.*, AVG(g.grade) AS avg_grade, COUNT(g.id) AS grades_count
        FROM students s LEFT JOIN grades g ON g.student_id = s.id
        {where}
        GROUP BY s.id
        ORDER BY s.name COLLATE NOCASE
    """
    if search:
        rows = db.execute(query.format(where="WHERE s.name LIKE ?"), (f"%{search}%",)).fetchall()
    else:
        rows = db.execute(query.format(where="")).fetchall()

    students = []
    for row in rows:
        s = dict_from_row(row)
        avg = s.pop("avg_grade")
        s["average"] = round(avg, 2) if avg is not None else None
        students.append(s)
    return jsonify(students)


@students_bp.route("/<int:student_id>", methods=["GET"])
def get_student(student_id):
    db = get_db()
    row = db.execute("SELECT * FROM students WHERE id = ?", (student_id,)).fetchone()
    if row is None:
        return jsonify({"error": t("err_student_not_found")}), 404

    student = dict_from_row(row)
    grade_rows = db.execute(
        "SELECT exam_id, grade FROM grades WHERE student_id = ?", (student_id,)
    ).fetchall()
    grades_by_exam = {g["exam_id"]: g["grade"] for g in grade_rows}

    subjects = []
    all_grades = []
    for subj in db.execute("SELECT * FROM subjects ORDER BY name COLLATE NOCASE").fetchall():
        exam_rows = db.execute(
            "SELECT * FROM exams WHERE subject_id = ? ORDER BY created_at, id", (subj["id"],)
        ).fetchall()
        if not exam_rows:
            continue

        exams = []
        subject_grades = []
        for exam in exam_rows:
            value = grades_by_exam.get(exam["id"])
            exams.append({"exam_id": exam["id"], "exam_name": exam["name"], "grade": value})
            if value is not None:
                subject_grades.append(value)
                all_grades.append(value)

        subjects.append({
            "subject_id": subj["id"],
            "subject_name": subj["name"],
            "exams": exams,
            "average": round(sum(subject_grades) / len(subject_grades), 2) if subject_grades else None,
        })

    overall = {
        "average": round(sum(all_grades) / len(all_grades), 2) if all_grades else None,
        "highest": max(all_grades) if all_grades else None,
        "lowest": min(all_grades) if all_grades else None,
        "exam_count": len(all_grades),
        "subject_count": len(subjects),
    }
    return jsonify({"student": student, "subjects": subjects, "overall": overall})


@students_bp.route("", methods=["POST"])
def create_student():
    data = request.get_json(silent=True) or {}
    name = (data.get("name") or "").strip()
    if not name:
        return jsonify({"error": t("err_student_name")}), 400

    db = get_db()
    cur = db.execute(
        "INSERT INTO students (name, class, section, notes) VALUES (?, ?, ?, ?)",
        (name, *_student_fields(data)),
    )
    db.commit()
    row = db.execute("SELECT * FROM students WHERE id = ?", (cur.lastrowid,)).fetchone()
    return jsonify(dict_from_row(row)), 201


@students_bp.route("/<int:student_id>", methods=["PUT"])
def update_student(student_id):
    db = get_db()
    if db.execute("SELECT id FROM students WHERE id = ?", (student_id,)).fetchone() is None:
        return jsonify({"error": t("err_student_not_found")}), 404

    data = request.get_json(silent=True) or {}
    name = (data.get("name") or "").strip()
    if not name:
        return jsonify({"error": t("err_student_name")}), 400

    db.execute(
        "UPDATE students SET name = ?, class = ?, section = ?, notes = ? WHERE id = ?",
        (name, *_student_fields(data), student_id),
    )
    db.commit()
    row = db.execute("SELECT * FROM students WHERE id = ?", (student_id,)).fetchone()
    return jsonify(dict_from_row(row))


@students_bp.route("/<int:student_id>", methods=["DELETE"])
def delete_student(student_id):
    db = get_db()
    if db.execute("SELECT id FROM students WHERE id = ?", (student_id,)).fetchone() is None:
        return jsonify({"error": t("err_student_not_found")}), 404

    db.execute("DELETE FROM students WHERE id = ?", (student_id,))
    db.commit()
    return jsonify({"message": t("student_deleted")})


# ===================== استيراد Excel =====================

def _detect_columns(first_row):
    """يرجع خريطة {الحقل: رقم العمود} إذا كان الصف الأول صف عناوين، وإلا None."""
    mapping = {}
    for idx, cell in enumerate(first_row):
        key = (_clean(cell) or "").lower()
        for field, aliases in HEADER_ALIASES.items():
            if key in aliases and field not in mapping:
                mapping[field] = idx
    return mapping if "name" in mapping else None


@students_bp.route("/import", methods=["POST"])
def import_students():
    upload = request.files.get("file")
    if upload is None or not upload.filename:
        return jsonify({"error": t("import_no_file")}), 400
    if not upload.filename.lower().endswith(".xlsx"):
        return jsonify({"error": t("import_bad_file")}), 400

    try:
        from openpyxl import load_workbook
        workbook = load_workbook(io.BytesIO(upload.read()), read_only=True, data_only=True)
        rows = [r for r in workbook.active.iter_rows(values_only=True, max_row=MAX_IMPORT_ROWS + 1)]
        workbook.close()
    except Exception:
        return jsonify({"error": t("import_bad_file")}), 400

    rows = [r for r in rows if r and any(_clean(c) for c in r)]
    if not rows:
        return jsonify({"error": t("import_no_names")}), 400

    mapping = _detect_columns(rows[0])
    if mapping:
        rows = rows[1:]
    else:
        mapping = {"name": 0}

    def cell(row, field):
        idx = mapping.get(field)
        return _clean(row[idx]) if idx is not None and idx < len(row) else None

    skip_duplicates = request.form.get("skip_duplicates", "1") == "1"
    db = get_db()
    existing = {r["name"].casefold() for r in db.execute("SELECT name FROM students").fetchall()}
    seen = set()
    added = 0
    skipped = []

    for row in rows:
        name = cell(row, "name")
        if not name:
            continue
        key = name.casefold()
        if key in seen:
            skipped.append({"name": name, "reason": t("reason_in_file")})
            continue
        seen.add(key)
        if skip_duplicates and key in existing:
            skipped.append({"name": name, "reason": t("reason_duplicate")})
            continue
        db.execute(
            "INSERT INTO students (name, class, section, notes) VALUES (?, ?, ?, ?)",
            (name, cell(row, "class"), cell(row, "section"), cell(row, "notes")),
        )
        added += 1

    if added == 0 and not skipped:
        return jsonify({"error": t("import_no_names")}), 400

    db.commit()
    return jsonify({
        "added": added,
        "skipped": len(skipped),
        "skipped_names": skipped[:50],
        "message": t("import_result", added=added, skipped=len(skipped)),
    })


@students_bp.route("/import-template", methods=["GET"])
def import_template():
    from openpyxl import Workbook
    from openpyxl.styles import Font

    workbook = Workbook()
    sheet = workbook.active
    sheet.title = t("tpl_sheet")
    sheet.append([t("tpl_name"), t("tpl_class"), t("tpl_section"), t("tpl_notes")])
    for c in sheet[1]:
        c.font = Font(bold=True)
    is_ar = get_lang() == "ar"
    examples = (
        [["أحمد محمد", "الصف العاشر", "أ", ""], ["زينب علي", "الصف العاشر", "ب", ""]]
        if is_ar else
        [["Sarah Ahmed", "Grade 10", "A", ""], ["Omar Ali", "Grade 10", "B", ""]]
    )
    for example in examples:
        sheet.append(example)
    for col, width in zip("ABCD", (28, 18, 12, 30)):
        sheet.column_dimensions[col].width = width
    sheet.sheet_view.rightToLeft = is_ar

    buffer = io.BytesIO()
    workbook.save(buffer)
    buffer.seek(0)
    return send_file(
        buffer,
        as_attachment=True,
        download_name="students_template.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
