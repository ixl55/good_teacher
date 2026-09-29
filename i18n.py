"""الترجمة: العربية والإنجليزية. اللغة تُحفظ في cookie باسم lang.
يحتوي أيضًا على قاعدة التحقق من الدرجة (رقم صحيح من 0 إلى 100)."""
from flask import request

SUPPORTED = ("ar", "en")
DEFAULT_LANG = "ar"

# key: (العربية, English)
STRINGS = {
    # ---------- عام ----------
    "app_title": ("سجل الدرجات", "Gradebook"),
    "brand_title": ("سجل الدرجات", "Gradebook"),
    "brand_subtitle": ("إدارة وتتبع الطلاب", "Track student progress"),
    "nav_main": ("القائمة الرئيسية", "Main menu"),
    "nav_dashboard": ("لوحة التحكم", "Dashboard"),
    "nav_students": ("الطلاب", "Students"),
    "nav_subjects": ("المواد", "Subjects"),
    "nav_exams": ("الامتحانات", "Exams"),
    "footer": ("سجل الدرجات — الإصدار 1.0", "Gradebook — v1.0"),
    "menu": ("القائمة", "Menu"),
    "search_placeholder": ("ابحث عن طالب، مادة، أو امتحان...", "Search students, subjects or exams..."),
    "toggle_theme": ("تبديل الوضع الداكن", "Toggle dark mode"),
    "switch_lang": ("English", "العربية"),
    "switch_lang_aria": ("Switch to English", "التبديل إلى العربية"),
    "edit": ("تعديل", "Edit"),
    "delete": ("حذف", "Delete"),
    "view": ("عرض", "View"),
    "open": ("فتح", "Open"),
    "cancel": ("إلغاء", "Cancel"),
    "save": ("حفظ", "Save"),
    "close": ("إغلاق", "Close"),
    "confirm_delete_title": ("تأكيد الحذف", "Confirm delete"),
    "confirm_default_msg": ("هل أنت متأكد؟ لا يمكن التراجع عن هذا الإجراء.", "Are you sure? This cannot be undone."),
    "server_unreachable": ("تعذر الاتصال بالخادم. تأكد من تشغيل التطبيق.", "Can't reach the server. Make sure the app is running."),
    "error_status": ("حدث خطأ ({n})", "Something went wrong ({n})"),
    "no_results": ("لا توجد نتائج مطابقة", "No matching results"),
    "average": ("المتوسط", "Average"),
    "grade": ("الدرجة", "Grade"),
    "no_grade": ("بدون درجة", "No grade"),

    # ---------- عناوين الصفحات ----------
    "dashboard_title": ("لوحة التحكم", "Dashboard"),
    "dashboard_subtitle": ("نظرة عامة على أداء الطلاب", "Overview of student performance"),
    "students_title": ("إدارة الطلاب", "Students"),
    "students_subtitle": ("إضافة، تعديل، وحذف بيانات الطلاب", "Add, edit and remove students"),
    "student_title": ("ملف الطالب", "Student profile"),
    "student_subtitle": ("المعدلات والتطور عبر الامتحانات", "Averages and progress across exams"),
    "subjects_title": ("إدارة المواد", "Subjects"),
    "subjects_subtitle": ("إضافة، تعديل، وحذف المواد الدراسية", "Add, edit and remove subjects"),
    "subject_title": ("ملف المادة", "Subject"),
    "subject_subtitle": ("الامتحانات والإحصائيات", "Exams and statistics"),
    "exam_title": ("إدارة درجات الامتحان", "Exam grades"),
    "exam_subtitle": ("أدخل درجة كل طالب واحفظ التغييرات", "Enter each student's grade, then save"),

    # ---------- لوحة التحكم ----------
    "overall_average": ("متوسط الدرجات العام", "Overall average"),
    "out_of_100": ("من 100", "out of 100"),
    "computed_from_all": ("محسوب من جميع الدرجات المسجلة", "Based on all recorded grades"),
    "computed_from_n": ("محسوب من {n} درجة مسجلة", "Recorded grades used: {n}"),
    "no_grades_yet": ("لا توجد درجات مسجلة بعد", "No grades recorded yet"),
    "legend_good": ("85 فأعلى", "85 and above"),
    "legend_mid": ("60 – 84", "60 – 84"),
    "legend_low": ("أقل من 60", "Below 60"),
    "stat_students": ("الطلاب", "Students"),
    "stat_subjects": ("المواد", "Subjects"),
    "stat_exams": ("الامتحانات", "Exams"),
    "stat_grades": ("الدرجات المسجلة", "Recorded grades"),
    "top_students": ("أفضل الطلاب", "Top students"),
    "sorted_by_avg": ("مرتبين حسب المعدل العام", "Ranked by overall average"),
    "subject_averages_chart": ("متوسط الدرجات حسب المادة", "Average grade by subject"),
    "recent_exams": ("آخر الامتحانات المضافة", "Recently added exams"),
    "not_enough_data": ("لا توجد بيانات كافية بعد", "Not enough data yet"),
    "no_exams_yet": ("لا توجد امتحانات مضافة بعد", "No exams added yet"),
    "enter_grades": ("إدخال الدرجات", "Enter grades"),

    # ---------- أعمدة الجداول ----------
    "col_student": ("الطالب", "Student"),
    "col_class": ("الصف", "Class"),
    "col_section": ("الشعبة", "Section"),
    "col_average": ("المعدل", "Average"),
    "col_exam": ("الامتحان", "Exam"),
    "col_exam_name": ("اسم الامتحان", "Exam name"),
    "col_subject": ("المادة", "Subject"),
    "col_grades_count": ("عدد الدرجات المسجلة", "Grades recorded"),
    "col_grades_n": ("عدد الدرجات", "Grades"),
    "col_exams_count": ("عدد الامتحانات", "Exams"),
    "col_avg_grade": ("متوسط الدرجات", "Average grade"),
    "col_created": ("تاريخ الإنشاء", "Created"),
    "col_added": ("تاريخ الإضافة", "Added"),
    "col_grade": ("الدرجة", "Grade"),

    # ---------- الطلاب ----------
    "students_list": ("قائمة الطلاب", "All students"),
    "search_by_name": ("البحث بالاسم...", "Search by name..."),
    "add_student": ("إضافة طالب", "Add student"),
    "no_students": ("لا يوجد طلاب بعد", "No students yet"),
    "no_students_hint": ("ابدأ بإضافة أول طالب، أو استورد القائمة من ملف Excel", "Add your first student, or import a list from Excel"),
    "load_students_failed": ("تعذر تحميل بيانات الطلاب", "Couldn't load students"),
    "modal_add_student": ("إضافة طالب جديد", "Add a new student"),
    "modal_edit_student": ("تعديل بيانات الطالب", "Edit student"),
    "field_name": ("الاسم الكامل", "Full name"),
    "ph_name": ("مثال: أحمد محمد", "e.g. Sarah Ahmed"),
    "field_class": ("الصف / المجموعة", "Class / group"),
    "ph_class": ("مثال: الصف العاشر", "e.g. Grade 10"),
    "field_section": ("الشعبة / القسم", "Section"),
    "ph_section": ("مثال: أ", "e.g. A"),
    "field_notes": ("ملاحظات (اختياري)", "Notes (optional)"),
    "ph_notes": ("أي ملاحظات إضافية...", "Any extra notes..."),
    "err_student_name_required": ("الرجاء إدخال اسم الطالب", "Please enter the student's name"),
    "student_updated": ("تم تحديث بيانات الطالب", "Student updated"),
    "student_added": ("تمت إضافة الطالب", "Student added"),
    "delete_student_title": ("حذف الطالب", "Delete student"),
    "delete_student_msg": ("هل أنت متأكد من حذف الطالب \"{name}\"؟ سيتم حذف جميع درجاته أيضًا.", "Delete \"{name}\"? All of their grades will be deleted too."),
    "student_deleted": ("تم حذف الطالب", "Student deleted"),

    # ---------- استيراد Excel ----------
    "import_excel": ("استيراد من Excel", "Import from Excel"),
    "import_title": ("استيراد الطلاب من Excel", "Import students from Excel"),
    "import_help": ("ارفع ملف ‎.xlsx‎ يحتوي على أسماء الطلاب. يتم التعرف على الأعمدة تلقائيًا.", "Upload an .xlsx file with your students' names. Columns are detected automatically."),
    "import_columns": ("الأعمدة المقبولة: الاسم، الصف، الشعبة، ملاحظات (بالعربية أو الإنجليزية). إذا لم توجد عناوين، يُعتبر العمود الأول هو الاسم.", "Recognised columns: Name, Class, Section, Notes (English or Arabic headers). With no header row, the first column is used as the name."),
    "download_template": ("تحميل ملف نموذجي", "Download template"),
    "choose_file": ("اختر ملف Excel", "Choose an Excel file"),
    "no_file_chosen": ("لم يتم اختيار ملف", "No file chosen"),
    "skip_duplicates": ("تخطي الأسماء الموجودة مسبقًا", "Skip names that already exist"),
    "import_btn": ("استيراد", "Import"),
    "import_no_file": ("الرجاء اختيار ملف Excel أولًا", "Please choose an Excel file first"),
    "import_result": ("تمت إضافة {added} طالب، وتم تخطي {skipped}.", "Students added: {added} · Skipped: {skipped}"),
    "import_bad_file": ("الملف غير صالح. استخدم ملف Excel بصيغة ‎.xlsx‎", "Invalid file. Please use an Excel .xlsx file"),
    "import_no_names": ("لم يتم العثور على أي أسماء في الملف", "No names were found in the file"),
    "import_skipped_rows": ("الأسماء التي تم تخطيها", "Skipped names"),
    "reason_duplicate": ("موجود مسبقًا", "already exists"),
    "reason_in_file": ("مكرر في الملف", "duplicated in file"),
    "tpl_name": ("الاسم", "Name"),
    "tpl_class": ("الصف", "Class"),
    "tpl_section": ("الشعبة", "Section"),
    "tpl_notes": ("ملاحظات", "Notes"),
    "tpl_sheet": ("الطلاب", "Students"),

    # ---------- ملف الطالب ----------
    "load_student_failed": ("تعذر تحميل بيانات الطالب", "Couldn't load this student"),
    "joined_on": ("انضم في {date}", "Joined {date}"),
    "overall_avg": ("المعدل العام", "Overall average"),
    "highest_grade": ("أعلى درجة", "Highest grade"),
    "lowest_grade": ("أقل درجة", "Lowest grade"),
    "exams_count": ("عدد الامتحانات", "Exams taken"),
    "subjects_count": ("عدد المواد", "Subjects"),
    "progress_title": ("تطور الطالب عبر الامتحانات", "Progress across exams"),
    "no_exams_for_student": ("لا توجد امتحانات لهذا الطالب بعد", "No exams for this student yet"),
    "no_exams_for_student_hint": ("أضف مادة وامتحانًا ثم سجل درجة الطالب لتظهر هنا", "Add a subject and an exam, then record a grade to see it here"),
    "avg_label": ("المعدل", "Average"),

    # ---------- المواد ----------
    "subjects_list": ("قائمة المواد", "All subjects"),
    "search_subject": ("البحث باسم المادة...", "Search subjects..."),
    "add_subject": ("إضافة مادة", "Add subject"),
    "no_subjects": ("لا توجد مواد بعد", "No subjects yet"),
    "no_subjects_hint": ("ابدأ بإضافة أول مادة دراسية", "Start by adding your first subject"),
    "load_subjects_failed": ("تعذر تحميل بيانات المواد", "Couldn't load subjects"),
    "modal_add_subject": ("إضافة مادة جديدة", "Add a new subject"),
    "modal_edit_subject": ("تعديل المادة", "Edit subject"),
    "field_subject_name": ("اسم المادة", "Subject name"),
    "ph_subject": ("مثال: الرياضيات", "e.g. Mathematics"),
    "err_subject_name_required": ("الرجاء إدخال اسم المادة", "Please enter the subject name"),
    "subject_updated": ("تم تحديث المادة", "Subject updated"),
    "subject_added": ("تمت إضافة المادة", "Subject added"),
    "delete_subject_title": ("حذف المادة", "Delete subject"),
    "delete_subject_msg": ("هل أنت متأكد من حذف مادة \"{name}\"؟ سيتم حذف جميع امتحاناتها ودرجاتها أيضًا.", "Delete \"{name}\"? All of its exams and grades will be deleted too."),
    "subject_deleted": ("تم حذف المادة", "Subject deleted"),
    "load_subject_failed": ("تعذر تحميل بيانات المادة", "Couldn't load this subject"),
    "added_on": ("تمت الإضافة في {date}", "Added {date}"),
    "students_avg_in_subject": ("متوسط الطلاب في المادة", "Class average"),
    "best_student": ("أفضل طالب", "Top student"),
    "worst_student": ("أقل طالب", "Lowest student"),
    "exams_heading": ("الامتحانات ({n})", "Exams ({n})"),
    "add_exam": ("إضافة امتحان", "Add exam"),
    "no_exams_in_subject": ("لا توجد امتحانات في هذه المادة بعد", "No exams in this subject yet"),
    "no_exams_in_subject_hint": ("اضغط على \"إضافة امتحان\" لإنشاء أول امتحان، ثم أدخل درجات الطلاب", "Click \"Add exam\" to create one, then enter your students' grades"),
    "manage_grades": ("إدارة الدرجات", "Manage grades"),
    "edit_name": ("تعديل الاسم", "Rename"),

    # ---------- الامتحانات ----------
    "modal_add_exam": ("إضافة امتحان جديد", "Add a new exam"),
    "modal_edit_exam": ("تعديل اسم الامتحان", "Rename exam"),
    "field_exam_name": ("اسم الامتحان", "Exam name"),
    "ph_exam": ("مثال: اختبار الشهر الأول", "e.g. Month 1 quiz"),
    "err_exam_name_required": ("الرجاء إدخال اسم الامتحان", "Please enter the exam name"),
    "exam_updated": ("تم تحديث الامتحان", "Exam updated"),
    "exam_added": ("تمت إضافة الامتحان، يمكنك الآن إدخال الدرجات", "Exam added — you can now enter grades"),
    "delete_exam": ("حذف الامتحان", "Delete exam"),
    "delete_exam_title": ("حذف الامتحان", "Delete exam"),
    "delete_exam_msg": ("هل أنت متأكد من حذف امتحان \"{name}\"؟ سيتم حذف جميع الدرجات المرتبطة به.", "Delete \"{name}\"? All grades for this exam will be deleted."),
    "exam_deleted": ("تم حذف الامتحان", "Exam deleted"),
    "load_exam_failed": ("تعذر تحميل بيانات الامتحان", "Couldn't load this exam"),
    "label_subject": ("المادة", "Subject"),
    "created_on": ("أُنشئ في {date}", "Created {date}"),
    "student_grades": ("درجات الطلاب ({n})", "Student grades ({n})"),
    "search_student": ("البحث عن طالب...", "Find a student..."),
    "no_students_system": ("لا يوجد طلاب مسجلين في النظام", "There are no students yet"),
    "no_students_system_hint": ("أضف طلابًا أولًا من صفحة إدارة الطلاب", "Add students first from the Students page"),
    "save_all_grades": ("حفظ جميع الدرجات", "Save all grades"),
    "grade_increase": ("زيادة الدرجة", "Increase grade"),
    "grade_decrease": ("إنقاص الدرجة", "Decrease grade"),
    "unsaved_n": ("يوجد {n} تعديل لم يُحفظ بعد", "{n} unsaved change(s)"),
    "grades_saved": ("تم حفظ جميع الدرجات", "All grades saved"),
    "exam_name_updated": ("تم تحديث اسم الامتحان", "Exam renamed"),
    "grade_range_hint": ("الدرجة رقم صحيح من 0 إلى 100 — اترك الحقل فارغًا إذا لم يدخل الطالب الامتحان", "Grades are whole numbers from 0 to 100 — leave blank if the student didn't sit the exam"),
    "invalid_grades_n": ("{n} درجة غير صالحة. يجب أن تكون رقمًا صحيحًا من 0 إلى 100.", "{n} grade(s) are invalid. Use a whole number from 0 to 100."),

    # ---------- رسائل الخادم ----------
    "err_not_found": ("المورد المطلوب غير موجود", "Not found"),
    "err_server": ("حدث خطأ في الخادم", "Server error"),
    "err_bad_payload": ("صيغة البيانات غير صحيحة", "Invalid request data"),
    "err_student_not_found": ("الطالب غير موجود", "Student not found"),
    "err_subject_not_found": ("المادة غير موجودة", "Subject not found"),
    "err_exam_not_found": ("الامتحان غير موجود", "Exam not found"),
    "err_grade_not_found": ("الدرجة غير موجودة", "Grade not found"),
    "err_student_name": ("اسم الطالب مطلوب", "Student name is required"),
    "err_subject_name": ("اسم المادة مطلوب", "Subject name is required"),
    "err_exam_name": ("اسم الامتحان مطلوب", "Exam name is required"),
    "err_subject_required": ("المادة مطلوبة", "Subject is required"),
    "err_subject_exists": ("توجد مادة بهذا الاسم مسبقًا", "A subject with this name already exists"),
    "err_student_exam_required": ("الطالب والامتحان مطلوبان", "Student and exam are required"),
    "err_grade_required": ("الدرجة مطلوبة", "Grade is required"),
    "err_grade_number": ("الدرجة يجب أن تكون رقمًا", "Grade must be a number"),
    "err_grade_range": ("الدرجة يجب أن تكون رقمًا صحيحًا من 0 إلى 100", "Grade must be a whole number from 0 to 100"),
    "err_grades_range_bulk": ("يوجد {n} درجة غير صالحة. كل درجة يجب أن تكون رقمًا صحيحًا من 0 إلى 100، ولم يتم حفظ أي شيء.", "{n} grade(s) are invalid. Every grade must be a whole number from 0 to 100 — nothing was saved."),
    "err_grade_exists": ("توجد درجة مسجلة مسبقًا لهذا الطالب في هذا الامتحان", "This student already has a grade for this exam"),
    "grade_deleted": ("تم حذف الدرجة", "Grade deleted"),
}

GRADE_MIN = 0
GRADE_MAX = 100


def get_lang():
    try:
        lang = request.cookies.get("lang", DEFAULT_LANG)
    except RuntimeError:
        return DEFAULT_LANG
    return lang if lang in SUPPORTED else DEFAULT_LANG


def t(key, lang=None, **params):
    lang = lang or get_lang()
    pair = STRINGS.get(key)
    if pair is None:
        return key
    text = pair[0] if lang == "ar" else pair[1]
    return text.format(**params) if params else text


def all_strings(lang):
    idx = 0 if lang == "ar" else 1
    return {k: v[idx] for k, v in STRINGS.items()}


def parse_grade(value):
    """يرجع (القيمة, مفتاح الخطأ). القيمة الفارغة ترجع (None, None)."""
    if value is None or value == "":
        return None, None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None, "err_grade_number"
    if number != number or not number.is_integer() or not (GRADE_MIN <= number <= GRADE_MAX):
        return None, "err_grade_range"
    return int(number), None
