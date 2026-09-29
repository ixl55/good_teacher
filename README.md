<p align="center"><img src="logo.png" alt="Gradebook" width="140"></p>

# Gradebook

## Why this project?

This project is built **for every local teacher** who wants to know their students as more than numbers in a notebook.

Many teachers record grades in paper notebooks or scattered spreadsheets, and the story gets lost. Who improved this month? Who is quietly falling behind? Who needs extra help before it's too late? These questions go unanswered, not because the information is missing, but because it's hard to see.

The idea is simple: **let the teacher see each student's progress, exam after exam.** That way you can notice early who is improving and encourage them, and who is slipping and support them. The goal isn't to collect grades. It's to **make sure every student gets better than they were**, and that no one gets forgotten in a busy classroom.

It's designed to be within reach of any teacher:

- **Free and private.** It runs on your own computer or on a small Raspberry Pi at home, and your students' data never leaves your home network.
- **Very simple.** Add an exam, the list of students appears, type the grades, save. That's it.
- **No limits.** Unlimited students, subjects and exams. One subject can have a single exam and another can have a hundred.
- **Works on your phone.** Enter grades from your phone right in the classroom.
- **Arabic and English**, switchable with one button.

---

## About the project

A local web app for managing students, subjects, exams and grades, with statistics and charts that show how each student is progressing.

**Features:**

- **Students:** add, edit, delete and search, plus **bulk import of names from an Excel file**.
- **Subjects and exams:** each subject can hold any number of exams, each with a name you choose.
- **Grade entry:** a list of all students for each exam, saved in one go. Grades are **whole numbers from 0 to 100**. The **− / +** buttons change a grade by 1 per press, and a student can be left without a grade.
- **Student profile:** average per subject, overall average, highest and lowest grade, and a chart of progress across exams.
- **Dashboard:** overall average, top students, average per subject, and recently added exams.
- **Interface:** Arabic (RTL) and English (LTR), light and dark mode, responsive design for phones.

**Tech stack:** Python + Flask for the server, SQLite for the database (a single `database.db` file), and a plain HTML/CSS/JavaScript front end with no framework, using Chart.js for charts.

---

## Getting started

Requires Python 3.9 or newer.

```bash
pip install -r requirements.txt
python app.py
```

Then open `http://127.0.0.1:5000` in your browser. The database is created automatically on first run.

On startup the app also prints an address like `http://192.168.1.15:5000`. Open it from any phone or computer on the same Wi-Fi network.

## Importing students from Excel

On the **Students** page, click **Import from Excel** and upload an `.xlsx` file.

- Columns are detected automatically: **Name, Class, Section, Notes**. Headers can be in English or Arabic (الاسم، الصف، الشعبة، ملاحظات).
- If the file has no header row, the first column is used as the student's name.
- Names that are duplicated within the file, or that already exist in the system, are skipped. You can turn this option off.
- A **Download template** button gives you a ready-to-fill file.

## Running on a Raspberry Pi at home

```bash
scp -r gred_mh pi@<raspberry-pi-address>:/home/pi/
cd /home/pi/gred_mh
pip3 install -r requirements.txt
python3 app.py
```

To start it automatically when the Pi boots, use the included systemd service in `deploy/gred_mh.service`:

```bash
sudo cp deploy/gred_mh.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now gred_mh
```

It's usually reachable at `http://raspberrypi.local:5000`.

> **Security note:** there is no password. The app is meant for a trusted home network only. Do not forward its port to the internet on your router.

> **Note:** the Chart.js library is loaded from the internet. On a network with no internet access every page still works, but charts won't be shown.

## Project structure

```
app.py              Entry point and page routes
i18n.py             Arabic/English UI text + grade validation (0–100)
database/models.py  Database schema
routes/             REST API (students, subjects, exams, grades, dashboard)
templates/          HTML pages
static/css, js      Styling and front-end logic
deploy/             Auto-start service for Raspberry Pi
```
