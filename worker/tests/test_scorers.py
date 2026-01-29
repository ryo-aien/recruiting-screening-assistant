import pytest

from worker.scorers.must_scorer import MustScorer
from worker.scorers.year_scorer import YearScorer
from worker.scorers.role_scorer import RoleScorer
from worker.scorers.nice_scorer import NiceScorer
from worker.scorers.total_fit_calculator import TotalFitCalculator


class TestMustScorer:
    def test_all_satisfied(self):
        scorer = MustScorer()
        job_requirements = {
            "must": [
                {"id": "m1", "text": "Python required", "skill_tags": ["Python"]},
                {"id": "m2", "text": "AWS required", "skill_tags": ["AWS"]},
            ]
        }
        candidate_profile = {
            "skills": ["Python", "AWS", "Docker"],
        }
        score, gaps = scorer.calculate(job_requirements, candidate_profile)
        assert score == 1.0
        assert len(gaps) == 0

    def test_partial_satisfied(self):
        scorer = MustScorer()
        job_requirements = {
            "must": [
                {"id": "m1", "text": "Python required", "skill_tags": ["Python"]},
                {"id": "m2", "text": "Go required", "skill_tags": ["Go"]},
            ]
        }
        candidate_profile = {
            "skills": ["Python", "JavaScript"],
        }
        score, gaps = scorer.calculate(job_requirements, candidate_profile)
        assert score == 0.5
        assert len(gaps) == 1
        assert "Go required" in gaps

    def test_no_requirements(self):
        scorer = MustScorer()
        job_requirements = {"must": []}
        candidate_profile = {"skills": ["Python"]}
        score, gaps = scorer.calculate(job_requirements, candidate_profile)
        assert score == 1.0
        assert len(gaps) == 0


class TestYearScorer:
    def test_meets_requirements(self):
        scorer = YearScorer()
        job_requirements = {
            "year_requirements": {"Python": 3, "AWS": 2}
        }
        candidate_profile = {
            "experience_years": {"Python": 5, "AWS": 3}
        }
        score = scorer.calculate(job_requirements, candidate_profile)
        assert score == 1.0

    def test_partial_requirements(self):
        scorer = YearScorer()
        job_requirements = {
            "year_requirements": {"Python": 5}
        }
        candidate_profile = {
            "experience_years": {"Python": 2.5}
        }
        score = scorer.calculate(job_requirements, candidate_profile)
        assert score == 0.5

    def test_no_requirements(self):
        scorer = YearScorer()
        job_requirements = {}
        candidate_profile = {"experience_years": {"Python": 5}}
        score = scorer.calculate(job_requirements, candidate_profile)
        assert score == 1.0


class TestRoleScorer:
    def test_exact_match(self):
        scorer = RoleScorer()
        job_requirements = {"role_expectation": "Lead"}
        candidate_profile = {"roles": ["Lead"]}
        score = scorer.calculate(job_requirements, candidate_profile)
        assert score == 1.0

    def test_adjacent_match(self):
        scorer = RoleScorer()
        job_requirements = {"role_expectation": "Lead"}
        candidate_profile = {"roles": ["IC"]}
        score = scorer.calculate(job_requirements, candidate_profile)
        assert score == 0.7

    def test_no_expectation(self):
        scorer = RoleScorer()
        job_requirements = {}
        candidate_profile = {"roles": ["IC"]}
        score = scorer.calculate(job_requirements, candidate_profile)
        assert score == 1.0


class TestTotalFitCalculator:
    def test_calculation(self):
        calculator = TotalFitCalculator()
        total = calculator.calculate(
            must_score=1.0,
            nice_score=0.8,
            year_score=0.6,
            role_score=1.0,
        )
        # 0.45*1.0 + 0.20*0.8 + 0.20*0.6 + 0.15*1.0 = 0.45 + 0.16 + 0.12 + 0.15 = 0.88
        assert total == 88

    def test_must_cap(self):
        calculator = TotalFitCalculator(must_cap_enabled=True, must_cap_value=20.0)
        total = calculator.calculate(
            must_score=0.5,
            nice_score=0.8,
            year_score=0.8,
            role_score=0.8,
            has_must_gaps=True,
        )
        assert total <= 20
