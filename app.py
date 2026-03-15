import os
import json
import pandas as pd
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from werkzeug.utils import secure_filename
from analysis import (
    calculate_statistics, get_grade_distribution, get_top_performers,
    get_bottom_performers, get_subject_analysis, get_pass_fail_stats,
    get_gender_analysis, get_attendance_analysis
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
UPLOAD_FOLDER = DATA_DIR
ALLOWED_EXTENSIONS = {'csv'}
DEFAULT_CSV = os.path.join(DATA_DIR, 'sample_students.csv')

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'outrix-student-analysis-dev-key')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB max

current_csv_path = DEFAULT_CSV
df_students = pd.DataFrame()


def load_data(path: str = None) -> pd.DataFrame:
    global df_students, current_csv_path
    target = path or current_csv_path
    try:
        df = pd.read_csv(target)
        required = [
            'student_id', 'name', 'age', 'gender', 'math_score',
            'english_score', 'science_score', 'history_score',
            'attendance_percentage', 'grade',
        ]
        for col in required:
            if col not in df.columns:
                raise ValueError(f"Missing column: {col}")
        df_students = df
        if path:
            current_csv_path = path
        return df
    except Exception:
        df_students = pd.DataFrame()
        return pd.DataFrame()


def allowed_file(filename: str) -> bool:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


load_data()


@app.route('/')
def index():
    stats = calculate_statistics(df_students)
    grade_dist = get_grade_distribution(df_students)
    top = get_top_performers(df_students, 5)
    bottom = get_bottom_performers(df_students, 5)
    pass_fail = get_pass_fail_stats(df_students)
    gender_analysis = get_gender_analysis(df_students)
    return render_template(
        'index.html',
        stats=stats,
        grade_dist=grade_dist,
        grade_dist_json=json.dumps(grade_dist),
        top_performers=top,
        bottom_performers=bottom,
        pass_fail=pass_fail,
        gender_analysis=gender_analysis,
        gender_analysis_json=json.dumps(gender_analysis),
    )


@app.route('/students')
def students():
    search = request.args.get('search', '').strip()
    grade_filter = request.args.get('grade', '').strip()
    gender_filter = request.args.get('gender', '').strip()
    sort_by = request.args.get('sort', 'student_id')
    sort_order = request.args.get('order', 'asc')

    data = df_students.copy()
    if not data.empty:
        score_cols = ['math_score', 'english_score', 'science_score', 'history_score']
        data['overall_score'] = data[score_cols].mean(axis=1).round(2)
        if search:
            mask = data['name'].str.contains(search, case=False, na=False)
            data = data[mask]
        if grade_filter:
            data = data[data['grade'] == grade_filter]
        if gender_filter:
            data = data[data['gender'] == gender_filter]
        valid_sort_cols = ['student_id', 'name', 'age', 'overall_score', 'attendance_percentage', 'grade']
        if sort_by in valid_sort_cols:
            ascending = sort_order == 'asc'
            data = data.sort_values(sort_by, ascending=ascending)

    students_list = data.to_dict(orient='records') if not data.empty else []
    grades = ['A', 'B', 'C', 'D', 'F']
    genders = df_students['gender'].unique().tolist() if not df_students.empty else ['Male', 'Female']

    return render_template(
        'students.html',
        students=students_list,
        grades=grades,
        genders=genders,
        search=search,
        grade_filter=grade_filter,
        gender_filter=gender_filter,
        sort_by=sort_by,
        sort_order=sort_order,
        total=len(students_list),
    )


@app.route('/student/<int:student_id>')
def student_detail(student_id):
    if df_students.empty:
        flash('No data loaded.', 'warning')
        return redirect(url_for('index'))
    row = df_students[df_students['student_id'] == student_id]
    if row.empty:
        flash(f'Student {student_id} not found.', 'danger')
        return redirect(url_for('students'))
    student = row.iloc[0].to_dict()
    score_cols = ['math_score', 'english_score', 'science_score', 'history_score']
    student['overall_score'] = round(sum(student[c] for c in score_cols) / len(score_cols), 2)
    all_scores = df_students[score_cols].mean(axis=1)
    rank = int((all_scores > student['overall_score']).sum()) + 1
    student['rank'] = rank
    student['total_students'] = len(df_students)
    subject_scores = {
        'Math': student['math_score'],
        'English': student['english_score'],
        'Science': student['science_score'],
        'History': student['history_score'],
    }
    class_avg = {
        'Math': round(float(df_students['math_score'].mean()), 2),
        'English': round(float(df_students['english_score'].mean()), 2),
        'Science': round(float(df_students['science_score'].mean()), 2),
        'History': round(float(df_students['history_score'].mean()), 2),
    }
    return render_template(
        'student_detail.html',
        student=student,
        subject_scores=subject_scores,
        subject_scores_json=json.dumps(subject_scores),
        class_avg=class_avg,
        class_avg_json=json.dumps(class_avg),
    )


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part in request.', 'danger')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No file selected.', 'danger')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(save_path)
            result = load_data(save_path)
            if result.empty:
                flash('File uploaded but could not be parsed. Check CSV format.', 'warning')
            else:
                flash(f'File "{filename}" uploaded successfully! Loaded {len(result)} students.', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid file type. Only CSV files are allowed.', 'danger')
            return redirect(request.url)
    return render_template('upload.html')


@app.route('/reports')
def reports():
    subject_analysis = get_subject_analysis(df_students)
    grade_dist = get_grade_distribution(df_students)
    pass_fail = get_pass_fail_stats(df_students)
    attendance_analysis = get_attendance_analysis(df_students)
    stats = calculate_statistics(df_students)

    subject_means = {k: v['mean'] for k, v in subject_analysis.items()}
    subject_scores_json = json.dumps({k: v['scores'] for k, v in subject_analysis.items()})

    return render_template(
        'reports.html',
        subject_analysis=subject_analysis,
        subject_means=subject_means,
        subject_means_json=json.dumps(subject_means),
        subject_scores_json=subject_scores_json,
        grade_dist=grade_dist,
        grade_dist_json=json.dumps(grade_dist),
        pass_fail=pass_fail,
        attendance_analysis=attendance_analysis,
        attendance_json=json.dumps(attendance_analysis.get('group_averages', {})),
        stats=stats,
    )


@app.route('/api/students')
def api_students():
    if df_students.empty:
        return jsonify([])
    score_cols = ['math_score', 'english_score', 'science_score', 'history_score']
    data = df_students.copy()
    data['overall_score'] = data[score_cols].mean(axis=1).round(2)
    return jsonify(data.to_dict(orient='records'))


@app.route('/api/statistics')
def api_statistics():
    stats = calculate_statistics(df_students)
    grade_dist = get_grade_distribution(df_students)
    pass_fail = get_pass_fail_stats(df_students)
    return jsonify({'statistics': stats, 'grade_distribution': grade_dist, 'pass_fail': pass_fail})


if __name__ == '__main__':
    debug_mode = os.environ.get('FLASK_DEBUG', '0') == '1'
    app.run(debug=debug_mode, host='0.0.0.0', port=5000)
