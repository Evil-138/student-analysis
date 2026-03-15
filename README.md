# Student Analysis Platform — Outrix Internship Project

A full-featured web application for analyzing student academic performance, built as part of the **Outrix** internship program. The platform ingests student data from CSV files and presents interactive dashboards, filterable tables, per-student detail views, and comprehensive statistical reports — all in a clean, responsive Bootstrap 5 interface.

The application is powered by **Flask** on the backend and uses **pandas** for data processing. Charts are rendered client-side with **Chart.js 4**, enabling rich visualizations without server-side image generation. A REST-like JSON API is also included so the data can be consumed by external tools or future front-end enhancements.

The project is structured to be easy to extend: new analysis functions slot neatly into `analysis.py`, new routes into `app.py`, and new pages into the Jinja2 template hierarchy under `templates/`.

---

## Features

- **Dashboard** — at-a-glance KPI cards (total students, average score, attendance, pass rate), grade-distribution pie chart, gender performance bar chart, and top/bottom performer tables.
- **Student List** — searchable, filterable (by grade and gender), sortable table of all students with colour-coded grades and attendance progress bars.
- **Student Detail** — individual profile page with radar chart comparing the student to the class average, subject score breakdown bar chart, and rank calculation.
- **Reports** — subject averages bar chart, grade distribution pie, pass/fail doughnut, attendance-bucket bar chart, full statistical table (mean, median, std, min, max per subject), and a correlation score between attendance and performance.
- **CSV Upload** — upload any conforming CSV to replace the active dataset, with format documentation and tips inline.
- **REST JSON API** — `/api/students` and `/api/statistics` endpoints for programmatic access.
- **Automated Tests** — pytest suite covering all analysis functions and all Flask routes.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Web framework | Flask 2.3 |
| Data processing | pandas 2.1, NumPy 1.25 |
| Charts | Chart.js 4.4 (CDN) |
| UI framework | Bootstrap 5.3 + Bootstrap Icons 1.11 (CDN) |
| Testing | pytest 7.4, pytest-flask 1.2 |
| Python | 3.9+ |

---

## Installation

```bash
# 1. Clone the repository
git clone <repository-url>
cd student-analysis

# 2. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the application
python app.py
```

The application will start at **http://localhost:5000**.

---

## Usage

1. Open `http://localhost:5000` in your browser — the dashboard loads with the bundled sample dataset (`data/sample_students.csv`).
2. Navigate to **Students** to browse, search, and filter the roster.
3. Click **View** on any student row to open their detail page with charts.
4. Visit **Reports** for aggregate analytics and subject statistics.
5. Go to **Upload** to replace the dataset with your own CSV file.

---

## Routes & API

| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | Dashboard |
| GET | `/students` | Student list (query params: `search`, `grade`, `gender`, `sort`, `order`) |
| GET | `/student/<id>` | Individual student detail |
| GET | `/upload` | Upload form |
| POST | `/upload` | Process CSV file upload |
| GET | `/reports` | Analytics & reports |
| GET | `/api/students` | JSON array of all students (includes `overall_score`) |
| GET | `/api/statistics` | JSON object with `statistics`, `grade_distribution`, `pass_fail` |

---

## CSV Format

The uploaded CSV must contain the following columns (header row required):

| Column | Type | Description |
|--------|------|-------------|
| `student_id` | Integer | Unique identifier |
| `name` | String | Full name |
| `age` | Integer | Age in years |
| `gender` | String | e.g. `Male` / `Female` |
| `math_score` | Float 0–100 | Mathematics score |
| `english_score` | Float 0–100 | English score |
| `science_score` | Float 0–100 | Science score |
| `history_score` | Float 0–100 | History score |
| `attendance_percentage` | Float 0–100 | Attendance percentage |
| `grade` | String | One of `A`, `B`, `C`, `D`, `F` |

**Example:**
```csv
student_id,name,age,gender,math_score,english_score,science_score,history_score,attendance_percentage,grade
1,Alice Johnson,18,Female,92,88,95,87,96.5,A
2,Bob Smith,19,Male,78,72,80,75,88.0,B
```

---

## Running Tests

```bash
python -m pytest tests/ -v
```

---

## Screenshots

> _Screenshots can be added here once the application is deployed or running locally._

---

## License

MIT License — © 2024 Outrix