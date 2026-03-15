import pandas as pd
import numpy as np
from typing import Dict, Any, List


def calculate_statistics(df: pd.DataFrame) -> Dict[str, Any]:
    """Calculate comprehensive statistics from student DataFrame."""
    if df.empty:
        return {
            'total_students': 0,
            'avg_math': 0,
            'avg_english': 0,
            'avg_science': 0,
            'avg_history': 0,
            'avg_overall': 0,
            'avg_attendance': 0,
            'highest_score': 0,
            'lowest_score': 0,
            'std_overall': 0,
            'median_overall': 0,
        }

    score_cols = ['math_score', 'english_score', 'science_score', 'history_score']
    df = df.copy()
    df['overall_score'] = df[score_cols].mean(axis=1)

    return {
        'total_students': len(df),
        'avg_math': round(float(df['math_score'].mean()), 2),
        'avg_english': round(float(df['english_score'].mean()), 2),
        'avg_science': round(float(df['science_score'].mean()), 2),
        'avg_history': round(float(df['history_score'].mean()), 2),
        'avg_overall': round(float(df['overall_score'].mean()), 2),
        'avg_attendance': round(float(df['attendance_percentage'].mean()), 2),
        'highest_score': round(float(df['overall_score'].max()), 2),
        'lowest_score': round(float(df['overall_score'].min()), 2),
        'std_overall': round(float(df['overall_score'].std()), 2),
        'median_overall': round(float(df['overall_score'].median()), 2),
    }


def get_grade_distribution(df: pd.DataFrame) -> Dict[str, int]:
    """Return count of each grade."""
    if df.empty:
        return {'A': 0, 'B': 0, 'C': 0, 'D': 0, 'F': 0}
    dist = df['grade'].value_counts().to_dict()
    for g in ['A', 'B', 'C', 'D', 'F']:
        dist.setdefault(g, 0)
    return {k: int(v) for k, v in dist.items()}


def get_top_performers(df: pd.DataFrame, n: int = 5) -> List[Dict]:
    """Return top n students by overall average score."""
    if df.empty:
        return []
    score_cols = ['math_score', 'english_score', 'science_score', 'history_score']
    df = df.copy()
    df['overall_score'] = df[score_cols].mean(axis=1).round(2)
    top = df.nlargest(n, 'overall_score')
    return top[['student_id', 'name', 'overall_score', 'grade', 'attendance_percentage']].to_dict(orient='records')


def get_bottom_performers(df: pd.DataFrame, n: int = 5) -> List[Dict]:
    """Return bottom n students by overall average score."""
    if df.empty:
        return []
    score_cols = ['math_score', 'english_score', 'science_score', 'history_score']
    df = df.copy()
    df['overall_score'] = df[score_cols].mean(axis=1).round(2)
    bottom = df.nsmallest(n, 'overall_score')
    return bottom[['student_id', 'name', 'overall_score', 'grade', 'attendance_percentage']].to_dict(orient='records')


def get_subject_analysis(df: pd.DataFrame) -> Dict[str, Dict]:
    """Return per-subject statistics."""
    if df.empty:
        return {}
    subjects = {
        'Math': 'math_score',
        'English': 'english_score',
        'Science': 'science_score',
        'History': 'history_score',
    }
    result = {}
    for label, col in subjects.items():
        result[label] = {
            'mean': round(float(df[col].mean()), 2),
            'median': round(float(df[col].median()), 2),
            'std': round(float(df[col].std()), 2),
            'min': round(float(df[col].min()), 2),
            'max': round(float(df[col].max()), 2),
            'scores': [float(x) for x in df[col].tolist()],
        }
    return result


def get_pass_fail_stats(df: pd.DataFrame) -> Dict[str, Any]:
    """Return pass/fail statistics (F = fail)."""
    if df.empty:
        return {'pass': 0, 'fail': 0, 'pass_rate': 0.0}
    fail_count = int((df['grade'] == 'F').sum())
    pass_count = len(df) - fail_count
    pass_rate = round(pass_count / len(df) * 100, 2)
    return {'pass': pass_count, 'fail': fail_count, 'pass_rate': pass_rate}


def get_gender_analysis(df: pd.DataFrame) -> Dict[str, Any]:
    """Return average scores broken down by gender."""
    if df.empty:
        return {}
    score_cols = ['math_score', 'english_score', 'science_score', 'history_score']
    df = df.copy()
    df['overall_score'] = df[score_cols].mean(axis=1)
    grouped = df.groupby('gender')['overall_score'].mean().round(2)
    return {str(k): float(v) for k, v in grouped.to_dict().items()}


def get_attendance_analysis(df: pd.DataFrame) -> Dict[str, Any]:
    """Correlate attendance with performance."""
    if df.empty:
        return {}
    score_cols = ['math_score', 'english_score', 'science_score', 'history_score']
    df = df.copy()
    df['overall_score'] = df[score_cols].mean(axis=1)
    correlation = round(float(df['attendance_percentage'].corr(df['overall_score'])), 3)
    bins = [0, 70, 80, 90, 100]
    labels = ['<70%', '70-80%', '80-90%', '90-100%']
    df['att_group'] = pd.cut(df['attendance_percentage'], bins=bins, labels=labels, include_lowest=True)
    group_avg = df.groupby('att_group', observed=True)['overall_score'].mean().round(2)
    group_avg_dict = {str(k): float(v) for k, v in group_avg.to_dict().items()}
    return {'correlation': correlation, 'group_averages': group_avg_dict}
