"""
طبقة الاتصال بقاعدة البيانات SQLite وإنشاء الجداول.
"""
import sqlite3
from flask import g, current_app

SCHEMA = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    class TEXT,
    section TEXT,
    notes TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime'))
);

CREATE TABLE IF NOT EXISTS subjects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    created_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime'))
);

CREATE TABLE IF NOT EXISTS exams (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    subject_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
    FOREIGN KEY (subject_id) REFERENCES subjects(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS grades (
{grades_columns}
);

CREATE INDEX IF NOT EXISTS idx_exams_subject ON exams(subject_id);
CREATE INDEX IF NOT EXISTS idx_grades_student ON grades(student_id);
CREATE INDEX IF NOT EXISTS idx_grades_exam ON grades(exam_id);
"""

GRADES_COLUMNS = """    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    exam_id INTEGER NOT NULL,
    grade REAL NOT NULL CHECK (grade BETWEEN 0 AND 100),
    created_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    FOREIGN KEY (exam_id) REFERENCES exams(id) ON DELETE CASCADE,
    UNIQUE (student_id, exam_id)"""

SCHEMA = SCHEMA.replace("{grades_columns}", GRADES_COLUMNS)


def _migrate_grades_range(db):
    """قواعد البيانات القديمة كانت تسمح بالدرجات من 1 فقط؛ نعيد بناء الجدول مع الحفاظ على البيانات."""
    row = db.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='grades'").fetchone()
    if row is None or "BETWEEN 0 AND 100" in row[0]:
        return
    db.execute("PRAGMA foreign_keys = OFF")
    db.executescript(f"""
        BEGIN;
        CREATE TABLE grades_new ({GRADES_COLUMNS});
        INSERT INTO grades_new (id, student_id, exam_id, grade, created_at, updated_at)
            SELECT id, student_id, exam_id, grade, created_at, updated_at FROM grades;
        DROP TABLE grades;
        ALTER TABLE grades_new RENAME TO grades;
        CREATE INDEX IF NOT EXISTS idx_grades_student ON grades(student_id);
        CREATE INDEX IF NOT EXISTS idx_grades_exam ON grades(exam_id);
        COMMIT;
    """)
    db.execute("PRAGMA foreign_keys = ON")


def get_db():
    """يرجع اتصال قاعدة بيانات مرتبط بطلب الـ request الحالي."""
    if "db" not in g:
        g.db = sqlite3.connect(current_app.config["DATABASE"])
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


def close_db(e=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db(app):
    """إنشاء الجداول إن لم تكن موجودة."""
    with app.app_context():
        db = get_db()
        db.executescript(SCHEMA)
        _migrate_grades_range(db)
        db.commit()
    app.teardown_appcontext(close_db)


def dict_from_row(row):
    if row is None:
        return None
    return dict(row)
