import pytest
from app.cases import BaseTestCase


@pytest.fixture
def base_test_case():
    return BaseTestCase("basetest", "app_commonapp", "Yes")


@pytest.mark.parametrize(
    "actual,expected", [("Yes", "Yes"), (1, "Yes"), ("None", ""), (None, "")]
)
def test_check_result(actual, expected, base_test_case):
    base_test_case.expected = expected
    assert base_test_case.check_result(actual)


def test_sql_join_clause(base_test_case):
    join_clause = "test join clause"
    base_test_case.join_clause = join_clause
    assert join_clause in base_test_case.sql


def test_sql_filters(base_test_case):
    base_test_case.filters = "foo = bar"
    assert base_test_case.filters in base_test_case.sql
