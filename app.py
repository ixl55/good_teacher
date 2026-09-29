"""
نقطة تشغيل التطبيق - نظام إدارة وتتبع درجات الطلاب.
تشغيل: python app.py
"""
import os
import sys
from flask import Flask, render_template, jsonify, request, redirect, make_response

import i18n

# لضمان طباعة النصوص العربية بشكل صحيح في الطرفية على ويندوز
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

from database import init_db

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def create_app():
    app = Flask(__name__)
    app.config["DATABASE"] = os.path.join(BASE_DIR, "database.db")
    app.config["JSON_AS_ASCII"] = False  # لدعم عرض النصوص العربية بشكل صحيح في JSON
    app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024  # حد حجم ملف Excel المرفوع

    init_db(app)

    # تسجيل الـ Blueprints الخاصة بالـ API
    from routes.students import students_bp
    from routes.subjects import subjects_bp
    from routes.exams import exams_bp
    from routes.grades import grades_bp
    from routes.dashboard import dashboard_bp

    app.register_blueprint(students_bp)
    app.register_blueprint(subjects_bp)
    app.register_blueprint(exams_bp)
    app.register_blueprint(grades_bp)
    app.register_blueprint(dashboard_bp)

    # ---------- اللغة ----------
    @app.context_processor
    def inject_i18n():
        lang = i18n.get_lang()
        return {
            "t": lambda key, **kw: i18n.t(key, lang, **kw),
            "lang": lang,
            "dir": "rtl" if lang == "ar" else "ltr",
            "js_strings": i18n.all_strings(lang),
        }

    @app.route("/lang/<code>")
    def set_language(code):
        target = request.args.get("next", "/")
        # منع إعادة التوجيه لمواقع خارجية
        if not target.startswith("/") or target.startswith("//"):
            target = "/"
        resp = make_response(redirect(target))
        if code in i18n.SUPPORTED:
            resp.set_cookie("lang", code, max_age=60 * 60 * 24 * 365, samesite="Lax")
        return resp

    # ---------- صفحات الواجهة ----------
    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/students")
    def students_page():
        return render_template("students.html")

    @app.route("/students/<int:student_id>")
    def student_details_page(student_id):
        return render_template("student-details.html", student_id=student_id)

    @app.route("/subjects")
    def subjects_page():
        return render_template("subjects.html")

    @app.route("/subjects/<int:subject_id>")
    def subject_details_page(subject_id):
        return render_template("subject-details.html", subject_id=subject_id)

    @app.route("/exams/<int:exam_id>")
    def exam_page(exam_id):
        return render_template("exam.html", exam_id=exam_id)

    # ---------- معالجة الأخطاء ----------
    @app.errorhandler(404)
    def not_found(e):
        if request.path.startswith("/api/"):
            return jsonify({"error": i18n.t("err_not_found")}), 404
        return render_template("index.html"), 404

    @app.errorhandler(500)
    def server_error(e):
        return jsonify({"error": i18n.t("err_server")}), 500

    return app


app = create_app()

if __name__ == "__main__":
    import socket

    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("DEBUG", "0") == "1"

    try:
        local_ip = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        local_ip.connect(("8.8.8.8", 80))
        lan_ip = local_ip.getsockname()[0]
        local_ip.close()
    except OSError:
        lan_ip = None

    print("=" * 50)
    print("  نظام إدارة وتتبع درجات الطلاب")
    print(f"  على هذا الجهاز: http://127.0.0.1:{port}")
    if lan_ip:
        print(f"  من أي جهاز آخر على نفس الشبكة: http://{lan_ip}:{port}")
    print("=" * 50)
    app.run(debug=debug, host=host, port=port)
