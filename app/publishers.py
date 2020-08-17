import re
from typing import List

import gspread

from .cases import BaseTestCase


def alias_converter(key):
    return re.sub(r"\s+", "_", key.lower())


class GoogleSheetsPublisher:
    def __init__(self, credential_path, sheet_key, worksheet_name=None):
        self.credential_path = credential_path
        self.sheet_key = sheet_key
        self.worksheet_name = worksheet_name
        self._client = None
        self._wks = None

    @classmethod
    def from_config(cls, config):
        return cls(
            config.GSPREAD_CREDENTIAL,
            config.GSPREAD_SHEET_KEY,
            config.GSPREAD_WORKSHEET_NAME,
        )

    def publish(self, test_results: List[BaseTestCase]):
        """Publish test results"""
        STATUS_COL = 2
        ACTUAL_COL = 8
        cells = []
        for result in test_results:
            idx = int(result.idx)
            status_cell = gspread.models.Cell(idx, STATUS_COL, result.status)
            actual_cell = gspread.models.Cell(idx, ACTUAL_COL, result.actual)
            cells.append(status_cell)
            cells.append(actual_cell)
        self.worksheet.update_cells(cells)

    def get_cases(self, statuses=["Untested", "Fail"], filter_func=None):
        records = self.worksheet.get_all_records(numericise_ignore=["all"])
        aliased = []
        for record in records:
            x = {}
            for k, v in record.items():
                alias = alias_converter(k)
                x[alias] = v
            aliased.append(x)
        filtered = filter(lambda z: z["status"] in statuses, aliased)
        if filter_func:
            filtered = filter(filter_func, filtered)
        return list(filtered)

    @property
    def client(self):
        if self._client is None:
            self._client = gspread.service_account(filename=self.credential_path)
        return self._client

    @property
    def worksheet(self):
        if self._wks is None:
            spreadsheet = self.client.open_by_key(self.sheet_key)
            if self.worksheet_name:
                self._wks = spreadsheet.worksheet(self.worksheet_name)
            else:
                self._wks = spreadsheet.get_worksheet(0)
        return self._wks
