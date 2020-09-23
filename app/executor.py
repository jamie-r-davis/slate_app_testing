from typing import List

from sqlalchemy import create_engine

from .cases import build_case
from .ps_cases import build_case as ps_build_case


class TestExecutor:
    def __init__(self, config, publisher):
        self.config = config
        self._db = None
        self.publisher = publisher
        self.results = []
        self.test_cases = []
        self.case_builder = (
            ps_build_case
            if config.TEST_PLAN == "peoplesoft" or config.TEST_MODE == "peoplesoft"
            else build_case
        )

    @property
    def db(self):
        if self._db is None:
            if self.config.TEST_MODE == "peoplesoft":
                db_url = self.config.PS_DB_URL
            else:
                db_url = self.config.DB_URL
            self._db = create_engine(db_url, echo=self.config.DEBUG)
        return self._db

    def add_result(self, test_case):
        self.results.append(test_case)

    def reset_results(self):
        self.results = []

    def add_test_case(self, test_case):
        self.test_cases.append(test_case)

    def get_test_cases(self, statuses=["Untested", "Fail", "Error"], filter_func=None):
        raw_cases = self.publisher.get_cases(statuses, filter_func)
        self.test_cases = [self.case_builder(**case) for case in raw_cases]

    def execute_case(self, test_case):
        test_case.execute(self.db)
        self.add_result(test_case)

    def run_tests(self):
        for test_case in self.test_cases:
            self.execute_case(test_case)

    def publish(self, reset=True):
        self.publisher.publish(self.results)
        if reset:
            self.reset_results()

    def run(self, filter_func=None, statuses: List[str] = None):
        statuses = statuses or ["Untested", "Fail", "Error"]
        self.get_test_cases(statuses, filter_func)
        self.run_tests()
        self.publish()
