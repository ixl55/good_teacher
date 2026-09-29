"""API إدارة المواد."""
import sqlite3
from flask import Blueprint, request, jsonify
from database import get_db, dict_from_row
from i18n import t

subjects_bp = Blueprint("subjects", __name__, url_prefix="/api/subjects")


@subjects_bp.route("", methods=["GET"])
def list_subjects():
    db = get_db()
    search = request.args.get("search", "").strip()
    if search:
        rows = db.execute(
            "SELECT * FROM subjects WHERE name LIKE ? ORDER BY name COLLATE NOCASE",
            (f"%{search}%",),
        ).fetchall()
    else:
        rows = db.execute("SELECT * FROM subjects ORDER BY name COLLATE NOCASE").fetchall()

    subjects = []
    for row in rows:
        s = dict_from_row(row)
        counts = db.execute(
            """
            SELECT
                (SELECT COUNT(*) FROM exams WHERE subject_id = ?) AS exams_count,
                (SELECT COUNT(*) FROM grades g JOIN exams e ON g.exam_id = e.id WHERE e.subject_id = ?) AS grades_count,
                (SELECT AVG(g.grade) FROM grades g JOIN exams e ON g.exam_id = e.id WHERE e.subject_id = ?) AS avg_grade
            """,
            (s["id"], s["id"], s["id"]),
        ).fetchone()
        s["exams_count"] = counts["exams_count"]
        s["grades_count"] = counts["grades_count"]
        s["average"] = round(counts["avg_grade"], 2) if counts["avg_grade"] is not None else None
        subjects.append(s)

    return jsonify(subjects)


@subjects_bp.route("/<int:subject_id>", methods=["GET"])
def get_subject(subject_id):
    db = get_db()
    row = db.execute("SELECT * FROM subjects WHERE id = ?", (subject_id,)).fetchone()
    if row is None:
        return jsonify({"error": t("err_subject_not_found")}), 404

    subject = dict_from_row(row)

    exam_rows = db.execute(
        "SELECT * FROM exams WHERE subject_id = ? ORDER BY created_at, id",
        (subject_id,),
    ).fetchall()

    exams = []
    for exam in exam_rows:
        stats = db.execute(
            "SELECT AVG(grade) AS avg_grade, COUNT(*) AS cnt FROM grades WHERE exam_id = ?",
            (exam["id"],),
        ).fetchone()
        exams.append({
            **dict_from_row(exam),
            "average": round(stats["avg_grade"], 2) if stats["avg_grade"] is not None else None,
            "grades_count": stats["cnt"],
        })

    # متوسط كل طالب في هذه المادة لإيجاد الأفضل والأقل
    student_avgs = db.execute(
        """
        SELECT s.id, s.name, AVG(g.grade) AS avg_grade
        FROM students s
        JOIN grades g ON g.student_id = s.id
        JOIN exams e ON g.exam_id = e.id
        WHERE e.subject_id = ?
        GROUP BY s.id
        """,
        (subject_id,),
    ).fetchall()

    best_student = None
    worst_student = None
    overall_avg = None
    if student_avgs:
        sorted_avgs = sorted(student_avgs, key=lambda r: r["avg_grade"])
        worst_row = sorted_avgs[0]
        best_row = sorted_avgs[-1]
        best_student = {"id": best_row["id"], "name": best_row["name"], "average": round(best_row["avg_grade"], 2)}
        worst_student = {"id": worst_row["id"], "name": worst_row["name"], "average": round(worst_row["avg_grade"], 2)}
        overall_avg = round(sum(r["avg_grade"] for r in student_avgs) / len(student_avgs), 2)

    return jsonify({
        "subject": subject,
        "exams": exams,
        "stats": {
            "exams_count": len(exams),
            "students_average": overall_avg,
            "best_student": best_student,
            "worst_student": worst_student,
        },
    })


@subjects_bp.route("/<int:subject_id>/exams", methods=["GET"])
def get_subject_exams(subject_id):
    db = get_db()
    subject = db.execute("SELECT * FROM subjects WHERE id = ?", (subject_id,)).fetchone()
    if subject is None:
        return jsonify({"error": t("err_subject_not_found")}), 404

    rows = db.execute(
        "SELECT * FROM exams WHERE subject_id = ? ORDER BY created_at, id",
        (subject_id,),
    ).fetchall()
    return jsonify([dict_from_row(r) for r in rows])


@subjects_bp.route("", methods=["POST"])
def create_subject():
    data = request.get_json(silent=True) or {}
    name = (data.get("name") or "").strip()
    if not name:
        return jsonify({"error": t("err_subject_name")}), 400

    db = get_db()
    try:
        cur = db.execute("INSERT INTO subjects (name) VALUES (?)", (name,))
        db.commit()
    except sqlite3.IntegrityError:
        return jsonify({"error": t("err_subject_exists")}), 409

    row = db.execute("SELECT * FROM subjects WHERE id = ?", (cur.lastrowid,)).fetchone()
    return jsonify(dict_from_row(row)), 201


@subjects_bp.route("/<int:subject_id>", methods=["PUT"])
def update_subject(subject_id):
    db = get_db()
    existing = db.execute("SELECT * FROM subjects WHERE id = ?", (subject_id,)).fetchone()
    if existing is None:
        return jsonify({"error": t("err_subject_not_found")}), 404

    data = request.get_json(silent=True) or {}
    name = (data.get("name") or "").strip()
    if not name:
        return jsonify({"error": t("err_subject_name")}), 400

    try:
        db.execute("UPDATE subjects SET name = ? WHERE id = ?", (name, subject_id))
        db.commit()
    except sqlite3.IntegrityError:
        return jsonify({"error": t("err_subject_exists")}), 409

    row = db.execute("SELECT * FROM subjects WHERE id = ?", (subject_id,)).fetchone()
    return jsonify(dict_from_row(row))


@subjects_bp.route("/<int:subject_id>", methods=["DELETE"])
def delete_subject(subject_id):
    db = get_db()
    existing = db.execute("SELECT * FROM subjects WHERE id = ?", (subject_id,)).fetchone()
    if existing is None:
        return jsonify({"error": t("err_subject_not_found")}), 404

    db.execute("DELETE FROM subjects WHERE id = ?", (subject_id,))
    db.commit()
    return jsonify({"message": t("subject_deleted")})
