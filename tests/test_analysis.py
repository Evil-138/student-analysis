"""
Tests for analysis.py — Outrix Student Analysis Platform
"""
import pytest
import pandas as pd
import numpy as np
from analysis import (
    calculate_statistics,
    get_grade_distribution,
    get_top_performers,
    get_bottom_performers,
    get_subject_analysis,
    get_pass_fail_stats,
    get_gender_analysis,
    get_attendance_analysis,
)


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def sample_df():
    """A small but representative student DataFrame."""
    data = {
        'student_id':           [1, 2, 3, 4, 5, 6, 7],
        'name':                 ['Alice', 'Bob', 'Carol', 'Dave', 'Eve', 'Frank', 'Grace'],
        'age':                  [18, 19, 18, 20, 19, 18, 20],
        'gender':               ['Female', 'Male', 'Female', 'Male', 'Female', 'Male', 'Female'],
        'math_score':           [92, 78, 55, 45, 88, 70, 60],
        'english_score':        [88, 72, 60, 48, 90, 65, 63],
        'science_score':        [95, 80, 58, 42, 92, 74, 57],
        'history_score':        [87, 75, 62, 50, 94, 69, 65],
        'attendance_percentage':[96.5, 88.0, 75.0, 65.0, 95.5, 82.0, 76.0],
        'grade':                ['A', 'B', 'D', 'F', 'A', 'C', 'C'],
    }
    return pd.DataFrame(data)


@pytest.fixture
def empty_df():
    return pd.DataFrame()


# ── calculate_statistics ──────────────────────────────────────────────────────

class TestCalculateStatistics:
    def test_returns_correct_keys(self, sample_df):
        stats = calculate_statistics(sample_df)
        expected_keys = {
            'total_students', 'avg_math', 'avg_english', 'avg_science',
            'avg_history', 'avg_overall', 'avg_attendance',
            'highest_score', 'lowest_score', 'std_overall', 'median_overall',
        }
        assert expected_keys == set(stats.keys())

    def test_total_students(self, sample_df):
        stats = calculate_statistics(sample_df)
        assert stats['total_students'] == 7

    def test_avg_math(self, sample_df):
        stats = calculate_statistics(sample_df)
        expected = round(float(sample_df['math_score'].mean()), 2)
        assert stats['avg_math'] == expected

    def test_avg_overall_in_range(self, sample_df):
        stats = calculate_statistics(sample_df)
        assert 0 <= stats['avg_overall'] <= 100

    def test_highest_gte_lowest(self, sample_df):
        stats = calculate_statistics(sample_df)
        assert stats['highest_score'] >= stats['lowest_score']

    def test_std_is_non_negative(self, sample_df):
        stats = calculate_statistics(sample_df)
        assert stats['std_overall'] >= 0

    def test_empty_df_returns_zeros(self, empty_df):
        stats = calculate_statistics(empty_df)
        assert stats['total_students'] == 0
        assert stats['avg_overall'] == 0
        assert stats['highest_score'] == 0


# ── get_grade_distribution ────────────────────────────────────────────────────

class TestGetGradeDistribution:
    def test_all_grades_present(self, sample_df):
        dist = get_grade_distribution(sample_df)
        for grade in ['A', 'B', 'C', 'D', 'F']:
            assert grade in dist

    def test_correct_counts(self, sample_df):
        dist = get_grade_distribution(sample_df)
        assert dist['A'] == 2
        assert dist['B'] == 1
        assert dist['C'] == 2
        assert dist['D'] == 1
        assert dist['F'] == 1

    def test_empty_df_all_zeros(self, empty_df):
        dist = get_grade_distribution(empty_df)
        assert all(v == 0 for v in dist.values())

    def test_values_are_integers(self, sample_df):
        dist = get_grade_distribution(sample_df)
        assert all(isinstance(v, int) for v in dist.values())


# ── get_top_performers ────────────────────────────────────────────────────────

class TestGetTopPerformers:
    def test_returns_correct_n(self, sample_df):
        top = get_top_performers(sample_df, n=3)
        assert len(top) == 3

    def test_sorted_descending(self, sample_df):
        top = get_top_performers(sample_df, n=5)
        scores = [s['overall_score'] for s in top]
        assert scores == sorted(scores, reverse=True)

    def test_required_keys(self, sample_df):
        top = get_top_performers(sample_df, n=2)
        for record in top:
            assert 'student_id' in record
            assert 'name' in record
            assert 'overall_score' in record
            assert 'grade' in record
            assert 'attendance_percentage' in record

    def test_empty_df_returns_empty_list(self, empty_df):
        assert get_top_performers(empty_df) == []

    def test_n_larger_than_df(self, sample_df):
        top = get_top_performers(sample_df, n=100)
        assert len(top) == len(sample_df)


# ── get_bottom_performers ─────────────────────────────────────────────────────

class TestGetBottomPerformers:
    def test_returns_correct_n(self, sample_df):
        bottom = get_bottom_performers(sample_df, n=3)
        assert len(bottom) == 3

    def test_sorted_ascending(self, sample_df):
        bottom = get_bottom_performers(sample_df, n=5)
        scores = [s['overall_score'] for s in bottom]
        assert scores == sorted(scores)

    def test_empty_df_returns_empty_list(self, empty_df):
        assert get_bottom_performers(empty_df) == []

    def test_top_and_bottom_no_overlap_when_n_small(self, sample_df):
        top = {s['student_id'] for s in get_top_performers(sample_df, n=2)}
        bottom = {s['student_id'] for s in get_bottom_performers(sample_df, n=2)}
        assert top.isdisjoint(bottom)


# ── get_subject_analysis ──────────────────────────────────────────────────────

class TestGetSubjectAnalysis:
    def test_all_subjects_present(self, sample_df):
        analysis = get_subject_analysis(sample_df)
        assert set(analysis.keys()) == {'Math', 'English', 'Science', 'History'}

    def test_each_subject_has_stats(self, sample_df):
        analysis = get_subject_analysis(sample_df)
        for subject, stats in analysis.items():
            assert 'mean' in stats
            assert 'median' in stats
            assert 'std' in stats
            assert 'min' in stats
            assert 'max' in stats
            assert 'scores' in stats

    def test_min_lte_max(self, sample_df):
        analysis = get_subject_analysis(sample_df)
        for subject, stats in analysis.items():
            assert stats['min'] <= stats['max'], f"{subject}: min > max"

    def test_scores_list_length(self, sample_df):
        analysis = get_subject_analysis(sample_df)
        for subject, stats in analysis.items():
            assert len(stats['scores']) == len(sample_df)

    def test_empty_df_returns_empty_dict(self, empty_df):
        assert get_subject_analysis(empty_df) == {}


# ── get_pass_fail_stats ───────────────────────────────────────────────────────

class TestGetPassFailStats:
    def test_pass_plus_fail_equals_total(self, sample_df):
        pf = get_pass_fail_stats(sample_df)
        assert pf['pass'] + pf['fail'] == len(sample_df)

    def test_pass_rate_calculation(self, sample_df):
        pf = get_pass_fail_stats(sample_df)
        expected_rate = round((pf['pass'] / len(sample_df)) * 100, 2)
        assert pf['pass_rate'] == expected_rate

    def test_fail_count_matches_grade_f(self, sample_df):
        pf = get_pass_fail_stats(sample_df)
        expected_fail = int((sample_df['grade'] == 'F').sum())
        assert pf['fail'] == expected_fail

    def test_pass_rate_between_0_and_100(self, sample_df):
        pf = get_pass_fail_stats(sample_df)
        assert 0.0 <= pf['pass_rate'] <= 100.0

    def test_empty_df(self, empty_df):
        pf = get_pass_fail_stats(empty_df)
        assert pf['pass'] == 0
        assert pf['fail'] == 0
        assert pf['pass_rate'] == 0.0


# ── get_gender_analysis ───────────────────────────────────────────────────────

class TestGetGenderAnalysis:
    def test_returns_present_genders(self, sample_df):
        result = get_gender_analysis(sample_df)
        assert 'Male' in result
        assert 'Female' in result

    def test_values_in_score_range(self, sample_df):
        result = get_gender_analysis(sample_df)
        for gender, avg in result.items():
            assert 0 <= avg <= 100, f"Average for {gender} out of range: {avg}"

    def test_empty_df_returns_empty_dict(self, empty_df):
        assert get_gender_analysis(empty_df) == {}

    def test_values_are_floats(self, sample_df):
        result = get_gender_analysis(sample_df)
        for val in result.values():
            assert isinstance(val, float)


# ── get_attendance_analysis ───────────────────────────────────────────────────

class TestGetAttendanceAnalysis:
    def test_has_correlation_key(self, sample_df):
        result = get_attendance_analysis(sample_df)
        assert 'correlation' in result

    def test_has_group_averages_key(self, sample_df):
        result = get_attendance_analysis(sample_df)
        assert 'group_averages' in result

    def test_correlation_in_valid_range(self, sample_df):
        result = get_attendance_analysis(sample_df)
        corr = result['correlation']
        assert -1.0 <= corr <= 1.0

    def test_group_averages_is_dict(self, sample_df):
        result = get_attendance_analysis(sample_df)
        assert isinstance(result['group_averages'], dict)

    def test_empty_df_returns_empty_dict(self, empty_df):
        assert get_attendance_analysis(empty_df) == {}
