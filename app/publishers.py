import re
from typing import List

import gspread

from .cases import BaseTestCase
from .utils import col_to_a1


def alias_converter(key):
    return re.sub(r"\s+", "_", key.lower())


class GoogleSheetsPublisher:
    def __init__(
        self, credential_path, sheet_key, worksheet_name=None, col_indexes=None
    ):
        self.credential_path = credential_path
        self.sheet_key = sheet_key
        self.worksheet_name = worksheet_name
        self._client = None
        self._wks = None
        self.col_indexes = col_indexes or {"status": 2, "actual": 9, "comment": 10}

    @classmethod
    def from_config(cls, config):
        return cls(
            credential_path=config.GSPREAD_CREDENTIAL,
            sheet_key=config.GSPREAD_SHEET_KEY,
            worksheet_name=config.GSPREAD_WORKSHEET_NAME,
            col_indexes=config.COL_INDEXES,
        )

    def publish(self, test_results: List[BaseTestCase]):
        """Publish test results"""
        status_col = self.col_indexes["status"]
        actual_col = self.col_indexes["actual"]
        cells = []
        for result in test_results:
            idx = int(result.idx)
            status_cell = gspread.models.Cell(idx, status_col, result.status)
            actual_cell = gspread.models.Cell(idx, actual_col, result.actual)
            cells.append(status_cell)
            cells.append(actual_cell)
        self.worksheet.update_cells(cells, value_input_option="RAW")

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

    def reset_tests(self):
        wks = self.worksheet
        status_col = self.col_indexes.get("status")
        actual_col = self.col_indexes.get("actual")
        cell_list = []
        for i, row in enumerate(wks.get_all_records()):
            idx = i + 2
            if row["Status"]:
                cell_list.append(gspread.models.Cell(idx, status_col, "Untested"))
            if row["Actual"]:
                cell_list.append(gspread.models.Cell(idx, actual_col, ""))
        wks.update_cells(cell_list, value_input_option="RAW")
