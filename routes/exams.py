"""API إدارة الامتحانات ودرجات الطلاب داخلها."""
from datetime import datetime
from flask import Blueprint, request, jsonify
from database import get_db, dict_from_row
from i18n import t, parse_grade

exams_bp = Blueprint("exams", __name__, url_prefix="/api/exams")


@exams_bp.route("", methods=["GET"])
def list_exams():
    db = get_db()
    search = request.args.get("search", "").strip()
    subject_id = request.args.get("subject_id")

    query = """
        SELECT e.*, s.name AS subject_name
        FROM exams e JOIN subjects s ON e.subject_id = s.id
        WHERE 1=1
    """
    params = []
    if search:
        query += " AND e.name LIKE ?"
        params.append(f"%{search}%")
    if subject_id:
        query += " AND e.subject_id = ?"
        params.append(subject_id)
    query += " ORDER BY e.created_at DESC, e.id DESC"

    rows = db.execute(query, params).fetchall()
    return jsonify([dict_from_row(r) for r in rows])


@exams_bp.route("/<int:exam_id>", methods=["GET"])
def get_exam(exam_id):
    """يرجع بيانات الامتحان مع قائمة الطلاب ودرجة كل واحد منهم (أو null)."""
    db = get_db()
    exam_row = db.execute(
        """
        SELECT e.*, s.name AS subject_name
        FROM exams e JOIN subjects s ON e.subject_id = s.id
        WHERE e.id = ?
        """,
        (exam_id,),
    ).fetchone()
    if exam_row is None:
        return jsonify({"error": t("err_exam_not_found")}), 404

    student_rows = db.execute("SELECT * FROM students ORDER BY name COLLATE NOCASE").fetchall()
    grade_rows = db.execute(
        "SELECT * FROM grades WHERE exam_id = ?", (exam_id,)
    ).fetchall()
    grades_by_student = {g["student_id"]: g for g in grade_rows}

    students = []
    for st in student_rows:
        g = grades_by_student.get(st["id"])
        students.append({
            "student_id": st["id"],
            "student_name": st["name"],
            "class": st["class"],
            "section": st["section"],
            "grade": g["grade"] if g else None,
            "grade_id": g["id"] if g else None,
        })

    return jsonify({"exam": dict_from_row(exam_row), "students": students})


@exams_bp.route("", methods=["POST"])
def create_exam():
    data = request.get_json(silent=True) or {}
    name = (data.get("name") or "").strip()
    subject_id = data.get("subject_id")

    if not name:
        return jsonify({"error": t("err_exam_name")}), 400
    if not subject_id:
        return jsonify({"error": t("err_subject_required")}), 400

    db = get_db()
    subject = db.execute("SELECT * FROM subjects WHERE id = ?", (subject_id,)).fetchone()
    if subject is None:
        return jsonify({"error": t("err_subject_not_found")}), 404

    cur = db.execute(
        "INSERT INTO exams (subject_id, name) VALUES (?, ?)", (subject_id, name)
    )
    db.commit()
    row = db.execute("SELECT * FROM exams WHERE id = ?", (cur.lastrowid,)).fetchone()
    return jsonify(dict_from_row(row)), 201


@exams_bp.route("/<int:exam_id>", methods=["PUT"])
def update_exam(exam_id):
    db = get_db()
    existing = db.execute("SELECT * FROM exams WHERE id = ?", (exam_id,)).fetchone()
    if existing is None:
        return jsonify({"error": t("err_exam_not_found")}), 404

    data = request.get_json(silent=True) or {}
    name = (data.get("name") or "").strip()
    if not name:
        return jsonify({"error": t("err_exam_name")}), 400

    db.execute("UPDATE exams SET name = ? WHERE id = ?", (name, exam_id))
    db.commit()
    row = db.execute("SELECT * FROM exams WHERE id = ?", (exam_id,)).fetchone()
    return jsonify(dict_from_row(row))


@exams_bp.route("/<int:exam_id>", methods=["DELETE"])
def delete_exam(exam_id):
    db = get_db()
    existing = db.execute("SELECT * FROM exams WHERE id = ?", (exam_id,)).fetchone()
    if existing is None:
        return jsonify({"error": t("err_exam_not_found")}), 404

    db.execute("DELETE FROM exams WHERE id = ?", (exam_id,))
    db.commit()
    return jsonify({"message": t("exam_deleted")})


@exams_bp.route("/<int:exam_id>/grades", methods=["GET"])
def get_exam_grades(exam_id):
    db = get_db()
    exam = db.execute("SELECT * FROM exams WHERE id = ?", (exam_id,)).fetchone()
    if exam is None:
        return jsonify({"error": t("err_exam_not_found")}), 404

    rows = db.execute(
        """
        SELECT g.*, s.name AS student_name
        FROM grades g JOIN students s ON g.student_id = s.id
        WHERE g.exam_id = ?
        ORDER BY s.name COLLATE NOCASE
        """,
        (exam_id,),
    ).fetchall()
    return jsonify([dict_from_row(r) for r in rows])


@exams_bp.route("/<int:exam_id>/grades", methods=["POST"])
def save_exam_grades(exam_id):
    """حفظ درجات جميع الطلاب لهذا الامتحان دفعة واحدة.
    Body: { "grades": [ {"student_id": 1, "grade": 85}, {"student_id": 2, "grade": null}, ... ] }
    grade = null أو غير موجودة => تترك بدون درجة (تحذف إن كانت موجودة).
    """
    db = get_db()
    exam = db.execute("SELECT * FROM exams WHERE id = ?", (exam_id,)).fetchone()
    if exam is None:
        return jsonify({"error": t("err_exam_not_found")}), 404

    data = request.get_json(silent=True) or {}
    items = data.get("grades", [])
    if not isinstance(items, list):
        return jsonify({"error": t("err_bad_payload")}), 400

    # التحقق من كل الدرجات أولًا: إذا كانت هناك أي درجة غير صالحة (خارج 0–100) لا يُحفظ شيء
    valid_ids = {r["id"] for r in db.execute("SELECT id FROM students").fetchall()}
    parsed = []
    invalid = []
    for item in items:
        if not isinstance(item, dict) or item.get("student_id") not in valid_ids:
            continue
        value, error = parse_grade(item.get("grade"))
        if error:
            invalid.append(item["student_id"])
        else:
            parsed.append((item["student_id"], value))

    if invalid:
        return jsonify({"error": t("err_grades_range_bulk", n=len(invalid)), "invalid_student_ids": invalid}), 400

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    saved = 0
    cleared = 0

    for student_id, grade_value in parsed:
        if grade_value is None:
            db.execute(
                "DELETE FROM grades WHERE student_id = ? AND exam_id = ?",
                (student_id, exam_id),
            )
            cleared += 1
            continue

        existing = db.execute(
            "SELECT id FROM grades WHERE student_id = ? AND exam_id = ?",
            (student_id, exam_id),
        ).fetchone()

        if existing:
            db.execute(
                "UPDATE grades SET grade = ?, updated_at = ? WHERE id = ?",
                (grade_value, now, existing["id"]),
            )
        else:
            db.execute(
                "INSERT INTO grades (student_id, exam_id, grade, updated_at) VALUES (?, ?, ?, ?)",
                (student_id, exam_id, grade_value, now),
            )
        saved += 1

    db.commit()
    return jsonify({"message": t("grades_saved"), "saved": saved, "cleared": cleared})
