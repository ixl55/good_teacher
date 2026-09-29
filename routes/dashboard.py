"""API لوحة التحكم الرئيسية والبحث العام."""
from flask import Blueprint, request, jsonify
from database import get_db, dict_from_row

dashboard_bp = Blueprint("dashboard", __name__, url_prefix="/api")


@dashboard_bp.route("/dashboard/stats", methods=["GET"])
def dashboard_stats():
    db = get_db()
    students_count = db.execute("SELECT COUNT(*) c FROM students").fetchone()["c"]
    subjects_count = db.execute("SELECT COUNT(*) c FROM subjects").fetchone()["c"]
    exams_count = db.execute("SELECT COUNT(*) c FROM exams").fetchone()["c"]
    grades_count = db.execute("SELECT COUNT(*) c FROM grades").fetchone()["c"]
    avg_row = db.execute("SELECT AVG(grade) a FROM grades").fetchone()
    overall_average = round(avg_row["a"], 2) if avg_row["a"] is not None else None

    return jsonify({
        "students_count": students_count,
        "subjects_count": subjects_count,
        "exams_count": exams_count,
        "grades_count": grades_count,
        "overall_average": overall_average,
    })


@dashboard_bp.route("/dashboard/top-students", methods=["GET"])
def top_students():
    db = get_db()
    limit = request.args.get("limit", 5, type=int)
    rows = db.execute(
        """
        SELECT s.id, s.name, s.class, s.section, AVG(g.grade) AS average, COUNT(g.id) AS grades_count
        FROM students s
        JOIN grades g ON g.student_id = s.id
        GROUP BY s.id
        ORDER BY average DESC
        LIMIT ?
        """,
        (limit,),
    ).fetchall()

    result = []
    for r in rows:
        d = dict_from_row(r)
        d["average"] = round(d["average"], 2)
        result.append(d)
    return jsonify(result)


@dashboard_bp.route("/dashboard/recent-exams", methods=["GET"])
def recent_exams():
    db = get_db()
    limit = request.args.get("limit", 5, type=int)
    rows = db.execute(
        """
        SELECT e.*, s.name AS subject_name,
            (SELECT COUNT(*) FROM grades g WHERE g.exam_id = e.id) AS grades_count
        FROM exams e JOIN subjects s ON e.subject_id = s.id
        ORDER BY e.created_at DESC, e.id DESC
        LIMIT ?
        """,
        (limit,),
    ).fetchall()
    return jsonify([dict_from_row(r) for r in rows])


@dashboard_bp.route("/dashboard/subject-averages", methods=["GET"])
def subject_averages():
    """متوسط الدرجات لكل مادة - يستخدم في رسم بياني بالـ Dashboard."""
    db = get_db()
    rows = db.execute(
        """
        SELECT sub.id, sub.name, AVG(g.grade) AS average, COUNT(g.id) AS grades_count
        FROM subjects sub
        LEFT JOIN exams e ON e.subject_id = sub.id
        LEFT JOIN grades g ON g.exam_id = e.id
        GROUP BY sub.id
        ORDER BY sub.name COLLATE NOCASE
        """
    ).fetchall()
    result = []
    for r in rows:
        d = dict_from_row(r)
        d["average"] = round(d["average"], 2) if d["average"] is not None else None
        result.append(d)
    return jsonify(result)


@dashboard_bp.route("/search", methods=["GET"])
def global_search():
    q = request.args.get("q", "").strip()
    if not q:
        return jsonify({"students": [], "subjects": [], "exams": []})

    db = get_db()
    like = f"%{q}%"

    students = db.execute(
        "SELECT id, name, class, section FROM students WHERE name LIKE ? LIMIT 10", (like,)
    ).fetchall()
    subjects = db.execute(
        "SELECT id, name FROM subjects WHERE name LIKE ? LIMIT 10", (like,)
    ).fetchall()
    exams = db.execute(
        """
        SELECT e.id, e.name, s.name AS subject_name, s.id AS subject_id
        FROM exams e JOIN subjects s ON e.subject_id = s.id
        WHERE e.name LIKE ? LIMIT 10
        """,
        (like,),
    ).fetchall()

    return jsonify({
        "students": [dict_from_row(r) for r in students],
        "subjects": [dict_from_row(r) for r in subjects],
        "exams": [dict_from_row(r) for r in exams],
    })
