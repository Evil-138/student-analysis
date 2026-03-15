"""
Tests for Flask routes — Outrix Student Analysis Platform
"""
import io
import json
import pytest
import pandas as pd

import app as app_module
from app import app as flask_app


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def client():
    flask_app.config['TESTING'] = True
    flask_app.config['WTF_CSRF_ENABLED'] = False
    with flask_app.test_client() as c:
        yield c


@pytest.fixture(autouse=True)
def load_sample_data():
    """Ensure the sample CSV is loaded before every test."""
    app_module.load_data(app_module.DEFAULT_CSV)
    yield


# ── Route: GET / ──────────────────────────────────────────────────────────────

class TestIndexRoute:
    def test_status_200(self, client):
        resp = client.get('/')
        assert resp.status_code == 200

    def test_contains_dashboard_heading(self, client):
        resp = client.get('/')
        assert b'Dashboard' in resp.data

    def test_contains_outrix_branding(self, client):
        resp = client.get('/')
        assert b'Outrix' in resp.data

    def test_stats_rendered(self, client):
        resp = client.get('/')
        assert b'Total Students' in resp.data or b'Avg' in resp.data


# ── Route: GET /students ──────────────────────────────────────────────────────

class TestStudentsRoute:
    def test_status_200(self, client):
        resp = client.get('/students')
        assert resp.status_code == 200

    def test_contains_table(self, client):
        resp = client.get('/students')
        assert b'<table' in resp.data

    def test_search_filter(self, client):
        resp = client.get('/students?search=Alice')
        assert resp.status_code == 200
        assert b'Alice' in resp.data

    def test_grade_filter(self, client):
        resp = client.get('/students?grade=A')
        assert resp.status_code == 200

    def test_gender_filter(self, client):
        resp = client.get('/students?gender=Female')
        assert resp.status_code == 200

    def test_sort_by_name(self, client):
        resp = client.get('/students?sort=name&order=asc')
        assert resp.status_code == 200

    def test_no_results_search(self, client):
        resp = client.get('/students?search=ZZZNOMATCH999')
        assert resp.status_code == 200
        assert b'No students match' in resp.data


# ── Route: GET /student/<id> ──────────────────────────────────────────────────

class TestStudentDetailRoute:
    def test_status_200_valid_student(self, client):
        resp = client.get('/student/1')
        assert resp.status_code == 200

    def test_student_name_shown(self, client):
        resp = client.get('/student/1')
        assert b'Alice Johnson' in resp.data

    def test_invalid_student_redirects(self, client):
        resp = client.get('/student/99999')
        assert resp.status_code == 302

    def test_contains_subject_scores(self, client):
        resp = client.get('/student/1')
        assert b'Math' in resp.data
        assert b'English' in resp.data
        assert b'Science' in resp.data
        assert b'History' in resp.data

    def test_contains_rank(self, client):
        resp = client.get('/student/1')
        assert b'Rank' in resp.data


# ── Route: GET /upload ────────────────────────────────────────────────────────

class TestUploadRoute:
    def test_status_200(self, client):
        resp = client.get('/upload')
        assert resp.status_code == 200

    def test_contains_file_input(self, client):
        resp = client.get('/upload')
        assert b'type="file"' in resp.data

    def test_contains_format_docs(self, client):
        resp = client.get('/upload')
        assert b'student_id' in resp.data

    def test_post_no_file_part_redirects(self, client):
        resp = client.post('/upload', data={})
        assert resp.status_code == 302

    def test_post_empty_filename_redirects(self, client):
        data = {'file': (io.BytesIO(b''), '')}
        resp = client.post('/upload', data=data, content_type='multipart/form-data')
        assert resp.status_code == 302

    def test_post_invalid_extension_redirects(self, client):
        data = {'file': (io.BytesIO(b'some data'), 'data.txt')}
        resp = client.post('/upload', data=data, content_type='multipart/form-data')
        assert resp.status_code == 302

    def test_post_valid_csv_redirects_to_index(self, client):
        csv_content = (
            b"student_id,name,age,gender,math_score,english_score,"
            b"science_score,history_score,attendance_percentage,grade\n"
            b"1,Test User,18,Female,80,75,85,70,90.0,B\n"
        )
        data = {'file': (io.BytesIO(csv_content), 'test_upload.csv')}
        resp = client.post('/upload', data=data, content_type='multipart/form-data')
        assert resp.status_code == 302
        assert '/upload' not in resp.headers.get('Location', '/upload')


# ── Route: GET /reports ───────────────────────────────────────────────────────

class TestReportsRoute:
    def test_status_200(self, client):
        resp = client.get('/reports')
        assert resp.status_code == 200

    def test_contains_charts(self, client):
        resp = client.get('/reports')
        assert b'subjectAvgChart' in resp.data
        assert b'gradeDistChart' in resp.data
        assert b'passfailChart' in resp.data

    def test_contains_subject_table(self, client):
        resp = client.get('/reports')
        assert b'Math' in resp.data
        assert b'Mean' in resp.data or b'mean' in resp.data.lower()

    def test_contains_pass_fail(self, client):
        resp = client.get('/reports')
        assert b'Pass' in resp.data
        assert b'Fail' in resp.data


# ── Route: GET /api/students ──────────────────────────────────────────────────

class TestApiStudentsRoute:
    def test_status_200(self, client):
        resp = client.get('/api/students')
        assert resp.status_code == 200

    def test_returns_json(self, client):
        resp = client.get('/api/students')
        assert resp.content_type == 'application/json'

    def test_returns_list(self, client):
        resp = client.get('/api/students')
        data = json.loads(resp.data)
        assert isinstance(data, list)

    def test_list_has_expected_length(self, client):
        resp = client.get('/api/students')
        data = json.loads(resp.data)
        assert len(data) == 25

    def test_student_record_has_overall_score(self, client):
        resp = client.get('/api/students')
        data = json.loads(resp.data)
        assert 'overall_score' in data[0]


# ── Route: GET /api/statistics ────────────────────────────────────────────────

class TestApiStatisticsRoute:
    def test_status_200(self, client):
        resp = client.get('/api/statistics')
        assert resp.status_code == 200

    def test_returns_json(self, client):
        resp = client.get('/api/statistics')
        assert resp.content_type == 'application/json'

    def test_has_statistics_key(self, client):
        resp = client.get('/api/statistics')
        data = json.loads(resp.data)
        assert 'statistics' in data

    def test_has_grade_distribution_key(self, client):
        resp = client.get('/api/statistics')
        data = json.loads(resp.data)
        assert 'grade_distribution' in data

    def test_has_pass_fail_key(self, client):
        resp = client.get('/api/statistics')
        data = json.loads(resp.data)
        assert 'pass_fail' in data

    def test_statistics_total_students(self, client):
        resp = client.get('/api/statistics')
        data = json.loads(resp.data)
        assert data['statistics']['total_students'] == 25
