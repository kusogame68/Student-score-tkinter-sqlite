# -*- coding: utf-8 -*-
"""
Created on Sat Jul  4 14:45:58 2026

@author: Johnson
"""

# Business Logic Module:
# - Score validation, average, grade level.

from typing import Dict, List, Tuple, Optional

class GradebookService:
    @staticmethod
    def validate_form(values: Dict[str, str]) -> Optional[str]:
        if any(val == '' for val in values.values()):
            return '請輸入完整資料!'
        return None

    @staticmethod
    def is_duplicate(student_id: str, existing: List[Tuple]) -> bool:
        return any(row[1] == student_id for row in existing)

    @staticmethod
    def validate_scores(values: Dict[str, str], subjects: Tuple[str, ...]) -> Tuple[Optional[str], List[float]]:
        scores = []
        for subject in subjects:
            score_str = values[subject]
            try:
                score = float(score_str)
            except ValueError:
                return f"{subject}必須是數字! (輸入: {score_str})", []

            if not 0 <= score <= 100:
                return f"{subject}分數必須在 0-100 之間 (輸入: {score})", []

            scores.append(score)
        return None, scores

    @staticmethod
    def validate_optional_scores(values: Dict[str, str], subjects: Tuple[str, ...]) -> Optional[str]:
        for subject in subjects:
            if values.get(subject):
                try:
                    score = float(values[subject])
                except ValueError:
                    return f"{subject}必須是數字! (輸入: {values[subject]})"

                if not 0 <= score <= 100:
                    return f"{subject}分數必須在 0-100 之間 (輸入: {score})"
        return None

    @staticmethod
    def compute_average(scores: List[float]) -> float:
        return round(sum(scores) / len(scores), 1)

    @staticmethod
    def get_grade_level(avg: float) -> str:
        thresholds = (
            (90, 'A+'), (85, 'A'), (80, 'A-'), (77, 'B+'), (73, 'B'),
            (70, 'B-'), (67, 'C+'), (63, 'C'), (60, 'C-'), (50, 'D'),
            (1, 'E')
        )
        return next((grade for threshold, grade in thresholds if avg >= threshold), 'X')