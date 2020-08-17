from dataclasses import dataclass
from datetime import datetime
from textwrap import dedent


class BaseTestCase:

    record = "base"
    base = "a"
    join_clause = ""

    def __init__(
        self,
        idx: str,
        external_id: str,
        field: str,
        export: str,
        expected: str,
        filters: str = None,
        **kwargs,
    ):
        self.idx = idx
        self.external_id = external_id
        self.field = field
        self.export = export
        self.expected = expected
        self.actual = None
        self.filters = None if filters is None else filters.replace('"', "'")
        self._status = kwargs.get("status")
        self._executed = False

    def __repr__(self):
        return f"<{self.__class__.__name__} idx={self.idx}>"

    @property
    def sql_export(self):
        return f"{self.base}.[{self.field}]"

    @property
    def sql(self):
        sql = f"""\
        select top 1
          {self.sql_export} as [actual]
        from application a
        join person p on a.[person] = p.[id]
        {self.join_clause}
        where
          a.[external_id] = '{self.external_id}'
        """
        if self.filters:
            sql += f" and {self.filters}"
        return dedent(sql)

    def store_result(self, actual):
        if isinstance(actual, datetime):
            actual = actual.strftime("%Y-%m-%d %H:%M:%S")
        self.actual = actual
        self._executed = True

    @property
    def passed(self):
        equivalencies = {
            "None": "",
            0: "No",
            1: "Yes",
            "1": "Yes",
            "0": "No",
            "Yes": "1",
            "No": "0",
            "N": "0",
            "Y": "1",
        }
        if str(self.actual) == self.expected:
            return True
        converted = equivalencies.get(str(self.actual), self.actual)
        if isinstance(converted, datetime):
            converted = converted.strftime("%Y-%m-%d %H:%M:%S")
        # handle shorthand syntax for longer responses
        if self.expected.endswith("..."):
            return converted.startswith(self.expected[:-3])
        return converted == self.expected

    def to_dict(self):
        return {
            "idx": self.idx,
            "status": self.status,
            "external_id": self.external_id,
            "field": self.field,
            "export": self.export,
            "expected": self.expected,
            "filters": self.filters,
        }

    @property
    def status(self):
        if self._executed:
            if self.passed:
                return "Pass"
            return "Fail"
        return "Untested"

    def execute(self, db):
        result = db.execute(self.sql).first()
        if result is None:
            actual = "### DOES NOT EXIST ###"
        else:
            actual = result.actual
        self.store_result(actual)


class FieldTestCase(BaseTestCase):
    @property
    def sql_export(self):
        exports = {
            "": f"(select string_agg([value], ', ') within group (order by [value]) from dbo.getfieldextendedmultitable({self.base}.[id], '{self.field}'))",
            "export 1": f"(select string_agg([value], ', ') within group (order by [value]) from dbo.getfieldexportmultitable({self.base}.[id], '{self.field}'))",
            "export 2": f"(select string_agg([value], ', ') within group (order by [value]) from dbo.getfieldexport2multitable({self.base}.[id], '{self.field}'))",
        }
        return exports[self.export.lower()]


class Application(BaseTestCase):
    base = "a"
    record = "application"


class ApplicationField(FieldTestCase):
    base = "a"
    record = "application field"


class Person(BaseTestCase):
    base = "p"
    record = "person"


class PersonField(FieldTestCase):
    base = "p"
    record = "person field"


class Relation(BaseTestCase):
    record = "relation"
    base = "r"
    join_clause = "join [relation] r on r.[record] = p.[id]"


class RelationField(FieldTestCase):
    record = "relation field"
    base = "r"
    join_clause = "join [relation] r on r.[record] = p.[id]"


class RelationSchool(BaseTestCase):
    record = "relation school"
    base = "rs"
    join_clause = "join [relation] r on r.[record] = p.[id]\njoin [school] rs on rs.[record] = r.[id]"


class School(BaseTestCase):
    record = "school"
    base = "s"
    join_clause = "join school s on s.[record] = p.[id]"


class TestScore(BaseTestCase):
    record = "test score"
    join_clause = "join [test] t on t.record = p.[id]\njoin [lookup.test] lt on t.[type] = lt.[id]"


def build_case(destination, **kwargs):
    destinations = {
        "application": Application,
        "application field": ApplicationField,
        "person": Person,
        "person field": PersonField,
        "school": School,
        "relation": Relation,
        "relation field": RelationField,
        "relation school": RelationSchool,
        "test score": TestScore,
    }
    destination_class = destinations[destination.lower()]
    return destination_class(**kwargs)
