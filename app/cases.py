import sys
import traceback
from datetime import date, datetime
from textwrap import dedent

from sqlalchemy.exc import DatabaseError, ProgrammingError


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
        self._exc = None

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} idx={self.idx}>"

    @property
    def sql_export(self) -> str:
        return f"{self.base}.[{self.field}]"

    @property
    def sql(self) -> str:
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

    def store_result(self, actual) -> None:
        if isinstance(actual, datetime):
            actual = actual.strftime("%Y-%m-%d %H:%M:%S")
        if isinstance(actual, str) and len(actual) > 100:
            actual = actual[:100]
        self.actual = actual
        self._executed = True

    @property
    def passed(self) -> bool:
        equivalencies = {
            "": "",
            " ": "",
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
        # allows for shorthand existence checking
        if self.expected == "### EXISTS ###":
            return self.actual != "### DOES NOT EXIST ###"
        converted = equivalencies.get(str(self.actual), self.actual)
        if isinstance(converted, datetime):
            converted = converted.strftime("%Y-%m-%d %H:%M:%S")
        # handle shorthand syntax for longer responses
        if self.expected.endswith("..."):
            return converted.startswith(self.expected[:-3])
        # handle cases where gsheets forced a comment on a numeric string
        if self.expected.startswith("'"):
            self.expected = self.expected[1:]
        # try to coerce expected to float and compare if actual is numeric
        if isinstance(self.actual, (float, int)):
            try:
                expected = float(self.expected)
            except:
                pass
            else:
                return expected == self.actual
        return converted == self.expected

    def to_dict(self) -> dict:
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
    def status(self) -> str:
        if self._exc:
            return "Error"
        if self._executed:
            if self.passed:
                return "Pass"
            return "Fail"
        return "Untested"

    def execute(self, db) -> None:
        try:
            result = db.execute(self.sql).first()
        except (DatabaseError, ProgrammingError) as e:
            type_, value_, traceback_ = sys.exc_info()
            exception = traceback.format_exception(
                type_, value_, traceback_, chain=True
            )
            actual = next(
                filter(lambda x: not x.startswith(" "), exception[1:])
            ).strip()
            self._exc = e
        else:
            if result is None:
                actual = "### DOES NOT EXIST ###"
            elif isinstance(result.actual, (datetime, date)):
                actual = result.actual.strftime("%Y-%m-%d %H:%M:%S")
            elif isinstance(result.actual, bool):
                actual = "1" if result.actual is True else "0"
            else:
                actual = result.actual
        finally:
            self.store_result(actual)


class FieldTestCase(BaseTestCase):
    @property
    def sql_export(self) -> str:
        exports = {
            "": f"(select string_agg([value], ', ') within group (order by [value]) from dbo.getfieldextendedmultitable({self.base}.[id], '{self.field}'))",
            "export 1": f"(select string_agg([value], ', ') within group (order by [value]) from dbo.getfieldexportmultitable({self.base}.[id], '{self.field}'))",
            "export 2": f"(select string_agg([value], ', ') within group (order by [value]) from dbo.getfieldexport2multitable({self.base}.[id], '{self.field}'))",
        }
        return exports[self.export.lower()]


class ApplicationActivity(BaseTestCase):
    base = "act"
    record = "activity"
    join_clause = "join [activity] act on a.[id] = act.[record]"


class Address(BaseTestCase):
    base = "ad"
    record = "address"
    join_clause = "join [address] ad on ad.[record] = p.[id]"


class Application(BaseTestCase):
    base = "a"
    record = "application"

    @property
    def sql_export(self) -> str:
        if self.field == "round":
            return "(select [name] from [lookup.round] where [id] = a.[round])"
        if self.field == "period":
            return "(select [name] from [lookup.period] where [id] = (select [period] from [lookup.round] where [id] = a.[round]))"
        return super().sql_export


class ApplicationField(FieldTestCase):
    base = "a"
    record = "application field"


class CBO(FieldTestCase):
    base = "cbo"
    record = "cbo entity"
    join_clause = "join [entity] cbo on cbo.[record] = a.[id] and cbo.[entity] = '684a173f-17fc-4f3d-bfe3-df2f1aedc79c'"


class Device(BaseTestCase):
    base = "d"
    record = "device"
    join_clause = "join [device] d on d.[record] = p.[id]"


class HonorsAndAwards(FieldTestCase):
    base = "awd"
    record = "honors and awards"
    join_clause = "join [entity] awd on awd.[record] = a.[id] and awd.[entity] = 'fba8d67b-f694-4e0d-b189-e3b8dfa2f869'"


class Interest(BaseTestCase):
    base = "int"
    record = "interests"
    join_clause = "join [interest] int on int.[record] = p.[id]"

    @property
    def sql_export(self) -> str:
        record_fields = [
            "name",
            "from",
            "to",
            "frequency",
            "description",
            "rank",
            "role",
            "city",
            "region",
            "country",
            "type",
            "frequency_hrs",
            "frequency_wks",
        ]
        exports = {
            "": f"(select string_agg([value], ', ') within group (order by [value]) from dbo.getfieldextendedmultitable({self.base}.[id], '{self.field}'))",
            "export 1": f"(select string_agg([value], ', ') within group (order by [value]) from dbo.getfieldexportmultitable({self.base}.[id], '{self.field}'))",
            "export 2": f"(select string_agg([value], ', ') within group (order by [value]) from dbo.getfieldexport2multitable({self.base}.[id], '{self.field}'))",
        }
        if self.field in record_fields:
            return super().sql_export
        return exports[self.export.lower()]


class InterestField(FieldTestCase):
    base = "int"
    record = "interests"
    join_clause = "join [interest] int on int.[record] = p.[id]"


class Person(BaseTestCase):
    base = "p"
    record = "person"

    @property
    def sql_export(self) -> str:
        if self.field == "ssn":
            return "case p.ssn when null then '' else 'XXX-XX-' + substring(p.ssn, 6, 4) end"
        return super().sql_export


class PersonField(FieldTestCase):
    base = "p"
    record = "person field"


class Relation(BaseTestCase):
    base = "r"
    record = "relation"
    join_clause = "join [relation] r on r.[record] = p.[id]"

    @property
    def sql_export(self) -> str:
        overridden_fields = ["education_level", "type"]
        if self.field in overridden_fields:
            return (
                f"(select [value] from [lookup.prompt] where [id] = r.[{self.field}])"
            )
        return super().sql_export


class RelationAddress(BaseTestCase):
    base = "ra"
    record = "relation address"
    join_clause = "join [relation] r on r.[record] = p.[id]\njoin [address] ra on ra.[record] = r.[id]"


class RelationField(FieldTestCase):
    base = "r"
    record = "relation field"
    join_clause = "join [relation] r on r.[record] = p.[id]"


class RelationJob(BaseTestCase):
    base = "rj"
    record = "relation job"
    join_clause = "join [relation] r on r.[record] = p.[id]\njoin [job] rj on rj.[record] = r.[id]"


class RelativeEmployee(FieldTestCase):
    base = "re"
    record = "relative employee"
    join_clause = "join [entity] re on a.[id] = re.[record] and re.[entity] = '84401b9b-bd17-4522-a1b5-c70ca539f659'"


class School(BaseTestCase):
    base = "s"
    record = "school"
    join_clause = "join school s on s.[record] = p.[id]"

    @property
    def sql_export(self) -> str:
        export = super().sql_export
        if self.field == "degree":
            return f"(select [value] from [lookup.prompt] where [id] = {export})"
        if self.field == "type":
            return f"case {export} when 'H' then 'High School' when 'U' then 'Undergraduate' when 'G' then 'Graduate' else null end"
        return export


class RelationSchool(School):
    base = "rs"
    record = "relation school"
    join_clause = "join [relation] r on r.[record] = p.[id]\njoin [school] rs on rs.[record] = r.[id]"


class TestScore(BaseTestCase):
    base = "t"
    record = "test score"
    join_clause = """
    cross apply (
      select
        x.[record],
        x.[type],
        x.[subtype],
        lt.[name],
        lt.[subname],
        x.[date],
        x.[confirmed],
        max(x.[total]) as total,
        max(x.[score1]) as score1,
        max(x.[score2]) as score2,
        max(x.[score3]) as score3,
        max(x.[score4]) as score4,
        max(x.[score5]) as score5,
        max(x.[score6]) as score6,
        max(x.[score7]) as score7,
        max(x.[score8]) as score8,
        max(x.[score9]) as score9,
        max(x.[score10]) as score10,
        max(x.[score11]) as score11,
        max(x.[score12]) as score12,
        max(x.[score13]) as score13,
        max(x.[score14]) as score14,
        max(x.[score15]) as score15,
        max(x.[score16]) as score16,
        max(x.[score17]) as score17
      from [test] x
        left join [lookup.test] lt on x.[type] = lt.[id] and x.[subtype] = lt.[subtype]
      where
        x.[record] = p.[id]
      group by x.[record], x.[type], x.[subtype], lt.[name], lt.[subname], x.[date], x.[confirmed]
    ) as t
    """


class CommonAppTransferAward(FieldTestCase):
    base = "e"
    record = "capx award"
    join_clause = "join [entity] e on e.[record] = a.[id] and e.[entity] = '82c27b15-8f87-429c-a8f8-453484a4a101'"


class CommonAppTansferHonor(FieldTestCase):
    base = "e"
    record = "capx hon"
    join_clause = "join [entity] e on e.[record] = a.[id] and e.[entity] = 'a2367bbe-37f6-4b23-aadd-1297bc7bbf26'"


class Job(BaseTestCase):
    base = "j"
    record = "job"
    join_clause = "join [job] j on j.[record] = p.[id]"


def build_case(destination: str, **kwargs) -> BaseTestCase:
    destinations = {
        "activity": ApplicationActivity,
        "address": Address,
        "application": Application,
        "application field": ApplicationField,
        "awards (capx)": CommonAppTransferAward,
        "cbos": CBO,
        "device": Device,
        "honors (capx)": CommonAppTansferHonor,
        "honors & awards": HonorsAndAwards,
        "job": Job,
        "interests": Interest,
        "interests field": InterestField,
        "person": Person,
        "person field": PersonField,
        "school": School,
        "relationship": Relation,
        "relationship address": RelationAddress,
        "relationship field": RelationField,
        "relationship job": RelationJob,
        "relationship school": RelationSchool,
        "relative employee": RelativeEmployee,
        "test scores": TestScore,
    }
    destination_class = destinations[destination.lower()]
    return destination_class(**kwargs)
