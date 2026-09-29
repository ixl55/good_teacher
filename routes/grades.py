"""API إدارة الدرجات الفردية."""
import sqlite3
from datetime import datetime
from flask import Blueprint, request, jsonify
from database import get_db, dict_from_row
from i18n import t, parse_grade

grades_bp = Blueprint("grades", __name__, url_prefix="/api/grades")


def _required_grade(value):
    """يرجع (القيمة, رسالة الخطأ) — الدرجة هنا إلزامية."""
    if value is None or value == "":
        return None, t("err_grade_required")
    number, error = parse_grade(value)
    return number, (t(error) if error else None)


@grades_bp.route("", methods=["GET"])
def list_grades():
    query = """
        SELECT g.*, st.name AS student_name, e.name AS exam_name, sub.name AS subject_name
        FROM grades g
        JOIN students st ON g.student_id = st.id
        JOIN exams e ON g.exam_id = e.id
        JOIN subjects sub ON e.subject_id = sub.id
        WHERE 1=1
    """
    params = []
    if request.args.get("student_id"):
        query += " AND g.student_id = ?"
        params.append(request.args["student_id"])
    if request.args.get("exam_id"):
        query += " AND g.exam_id = ?"
        params.append(request.args["exam_id"])
    query += " ORDER BY g.updated_at DESC"
    return jsonify([dict_from_row(r) for r in get_db().execute(query, params).fetchall()])


@grades_bp.route("", methods=["POST"])
def create_grade():
    data = request.get_json(silent=True) or {}
    student_id = data.get("student_id")
    exam_id = data.get("exam_id")
    if not student_id or not exam_id:
        return jsonify({"error": t("err_student_exam_required")}), 400

    grade, error = _required_grade(data.get("grade"))
    if error:
        return jsonify({"error": error}), 400

    db = get_db()
    if db.execute("SELECT id FROM students WHERE id = ?", (student_id,)).fetchone() is None:
        return jsonify({"error": t("err_student_not_found")}), 404
    if db.execute("SELECT id FROM exams WHERE id = ?", (exam_id,)).fetchone() is None:
        return jsonify({"error": t("err_exam_not_found")}), 404

    try:
        cur = db.execute(
            "INSERT INTO grades (student_id, exam_id, grade) VALUES (?, ?, ?)",
            (student_id, exam_id, grade),
        )
        db.commit()
    except sqlite3.IntegrityError:
        return jsonify({"error": t("err_grade_exists")}), 409

    row = db.execute("SELECT * FROM grades WHERE id = ?", (cur.lastrowid,)).fetchone()
    return jsonify(dict_from_row(row)), 201


@grades_bp.route("/<int:grade_id>", methods=["PUT"])
def update_grade(grade_id):
    db = get_db()
    if db.execute("SELECT id FROM grades WHERE id = ?", (grade_id,)).fetchone() is None:
        return jsonify({"error": t("err_grade_not_found")}), 404

    data = request.get_json(silent=True) or {}
    grade, error = _required_grade(data.get("grade"))
    if error:
        return jsonify({"error": error}), 400

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    db.execute("UPDATE grades SET grade = ?, updated_at = ? WHERE id = ?", (grade, now, grade_id))
    db.commit()
    row = db.execute("SELECT * FROM grades WHERE id = ?", (grade_id,)).fetchone()
    return jsonify(dict_from_row(row))


@grades_bp.route("/<int:grade_id>", methods=["DELETE"])
def delete_grade(grade_id):
    db = get_db()
    if db.execute("SELECT id FROM grades WHERE id = ?", (grade_id,)).fetchone() is None:
        return jsonify({"error": t("err_grade_not_found")}), 404

    db.execute("DELETE FROM grades WHERE id = ?", (grade_id,))
    db.commit()
    return jsonify({"message": t("grade_deleted")})
