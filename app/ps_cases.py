from decimal import Decimal
from textwrap import dedent

from .cases import BaseTestCase


class PSTestCase(BaseTestCase):
    def __init__(
        self,
        idx: str,
        adm_appl_nbr: str,
        field: str,
        expected: str,
        export: str = "",
        filters: str = None,
        **kwargs,
    ):
        super().__init__(idx, adm_appl_nbr, field, export, expected, filters)
        self.adm_appl_nbr = adm_appl_nbr
        self.kwargs = kwargs

    @property
    def sql_export(self) -> str:
        return f"{self.base}.{self.field}"

    @property
    def sql(self) -> str:
        sql = f"""\
            select
              {self.sql_export} as actual
            from ps_adm_appl_data a
            {self.join_clause}
            where
              a.adm_appl_nbr = '{self.adm_appl_nbr}'"""
        if self.filters:
            sql += f" and {self.filters}"
        return dedent(sql)

    def store_result(self, actual) -> None:
        # oracle db stores floats as Decimal, so cast it as a float
        if isinstance(actual, Decimal):
            actual = float(actual)
        super().store_result(actual)


class AdmApplData(PSTestCase):
    record = "ps_adm_appl_data"
    base = "a"


class AdmApplProg(PSTestCase):
    record = "ps_adm_appl_prog"
    base = "prg"
    join_clause = dedent(
        """\
        join ps_adm_appl_prog prg on 
          a.emplid = prg.emplid and
          a.adm_appl_nbr = prg.adm_appl_nbr and
          a.stdnt_car_nbr = prg.stdnt_car_nbr and
          a.acad_career = prg.acad_career and
          prg.effdt = (
            select max(effdt)
            from ps_adm_appl_prog
            where
              emplid = prg.emplid and
              adm_appl_nbr = prg.adm_appl_nbr and
              stdnt_car_nbr = prg.stdnt_car_nbr and
              acad_career = prg.acad_career and
              effdt <= sysdate
          ) and
          prg.effseq = (
            select max(effseq)
            from ps_adm_appl_prog
            where
              emplid = prg.emplid and
              adm_appl_nbr = prg.adm_appl_nbr and
              stdnt_car_nbr = prg.stdnt_car_nbr and
              acad_career = prg.acad_career and
              effdt = prg.effdt
          )
        left join ps_adm_appl_plan pln on
          pln.emplid = prg.emplid and
          pln.ADM_APPL_NBR = prg.ADM_APPL_NBR and
          pln.ACAD_CAREER = prg.acad_career and
          pln.STDNT_CAR_NBR = prg.stdnt_car_nbr and
          pln.appl_prog_nbr = prg.appl_prog_nbr and
          pln.effdt = prg.effdt and
          pln.effseq = prg.effseq
        left join ps_adm_appl_sbplan s on
          s.emplid = pln.emplid and
          s.adm_appl_nbr = pln.adm_appl_nbr and
          s.acad_career = pln.acad_career and
          s.appl_prog_nbr = pln.appl_prog_nbr and
          s.effdt = pln.effdt and
          s.effseq = pln.effseq and
          s.acad_plan = pln.acad_plan"""
    )

    @property
    def sql_export(self) -> str:
        if self.field == "acad_plan":
            return "pln.acad_plan"
        if self.field == "acad_sub_plan":
            return "sbp.acad_sub_plan"
        return super().sql_export


class PrimaryName(PSTestCase):
    record = "ps_names"
    base = "n"
    join_clause = dedent(
        """\
        join ps_names n on 
          a.emplid = n.emplid and
          n.name_type = 'PRI' and 
          n.effdt = (select max(effdt) from ps_names where emplid = n.emplid and name_type = n.name_type)
        """
    )


class OtherName(PSTestCase):
    record = "ps_names"
    base = "n"
    join_clause = dedent(
        """\
        join ps_names n on 
          a.emplid = n.emplid and
          n.name_type = 'OTH' and 
          n.effdt = (select max(effdt) from ps_names where emplid = n.emplid and name_type = n.name_type)
        """
    )


class CurrentAddress(PSTestCase):
    record = "ps_person_address"
    base = "ad"
    join_clause = dedent(
        """\
        join ps_addresses ad on
          a.emplid = ad.emplid and
          ad.address_type = 'CURR' and
          ad.effdt = (select max(effdt) from ps_addresses where emplid = ad.emplid and address_type = ad.address_type)
        """
    )

    @property
    def sql_export(self) -> str:
        if self.field == "country":
            return "(select descr from ps_country_tbl where country = ad.country)"
        return super().sql_export


class PermanentAddress(PSTestCase):
    record = "ps_addresses"
    base = "ad"
    join_clause = dedent(
        """\
        join ps_addresses ad on
          a.emplid = ad.emplid and
          ad.address_type = 'PERM' and
          ad.effdt = (select max(effdt) from ps_addresses where emplid = ad.emplid and address_type = ad.address_type)
        """
    )

    @property
    def sql_export(self) -> str:
        if self.field == "country":
            return "(select descr from ps_country_tbl where country = ad.country)"
        return super().sql_export


class Person(PSTestCase):
    record = "ps_person"
    base = "p"
    join_clause = "join ps_person p on a.emplid = p.emplid"

    @property
    def sql_export(self) -> str:
        if self.field == "birthcountry":
            return "(select descr from ps_country_tbl where country = p.birthcountry)"
        return super().sql_export


class PersonDataEffdt(PSTestCase):
    record = "ps_pers_data_effdt"
    base = "pde"
    join_clause = dedent(
        """\
        join ps_pers_data_effdt pde on 
          a.emplid = pde.emplid and 
          pde.effdt = (select max(effdt) from ps_pers_data_effdt where emplid = pde.emplid)
        """
    )


class Phone(PSTestCase):
    record = "ps_personal_phone"
    base = "p"
    join_clause = "join ps_personal_phone p on a.emplid = p.emplid"


class AdditionalData(PSTestCase):
    record = "ps_m_ra_adl_data"
    base = "adl"
    join_clause = dedent(
        """\
        join ps_m_ra_adl_data adl on 
          a.emplid = adl.emplid and 
          a.adm_appl_nbr = adl.adm_appl_nbr and 
          a.acad_career = adl.acad_career and 
          a.stdnt_car_nbr = adl.stdnt_car_nbr
        join ps_m_ra_adldata_tb q on
          adl.m_ra_question_id = q.m_ra_question_id and
          q.adm_appl_ctr = a.adm_appl_ctr
        """
    )

    @property
    def sql_export(self) -> str:
        question_fields = ["descr", "label", "category"]
        if self.field in question_fields:
            return f"q.{self.field}"
        return super().sql_export


class NationalID(PSTestCase):
    record = "ps_pers_nid"
    base = "nid"
    join_clause = "join ps_pers_nid nid on a.emplid = nid.emplid"

    @property
    def sql_export(self) -> str:
        if self.field == "national_id":
            return "regexp_replace(national_id, '^[0-9]{5}', 'XXXXX')"
        return super().sql_export


class Citizenship(PSTestCase):
    record = "ps_citizenship"
    base = "c"
    join_clause = "join ps_citizenship c on a.emplid = c.emplid"


class Visa(PSTestCase):
    record = "ps_visa_pmt_data"
    base = "v"
    join_clause = dedent(
        """\
        join ps_visa_pmt_data v on 
            a.emplid = v.emplid and 
            v.effdt = (
                select max(effdt) 
                from ps_visa_pmt_data v 
                where 
                    emplid = v.emplid and
                    visa_permit_type = v.visa_permit_type and
                    country = v.country
            )
        """
    )


class Ethnicity(PSTestCase):
    record = "ps_ethnicity_dtl"
    base = "e"
    join_clause = dedent(
        """
        outer apply (
          select
            listagg(ethnic_grp_cd, ', ') within group (order by ethnic_grp_cd) as ethnic_grp_cd,
            max(HISP_LATINO) as hisp_latino
          from PS_ETHNICITY_DTL x
          where
            x.emplid = a.emplid
        ) e
        """
    )


class School(PSTestCase):
    record = "ps_ext_acad_data"
    base = "s"
    join_clause = (
        "join ps_ext_acad_data s on a.emplid = s.emplid and s.ext_data_nbr = 1"
    )


class RatingComponent(PSTestCase):
    record = "ps_adm_appl_cmp"
    base = "r"
    join_clause = dedent(
        """\
        join ps_adm_appl_cmp r on 
          r.adm_appl_nbr = a.adm_appl_nbr and 
          r.emplid = a.emplid and 
          r.acad_career = a.acad_career and 
          r.stdnt_car_nbr = a.stdnt_car_nbr
        """
    )


class EvaluationCode(PSTestCase):
    record = "ps_adm_appl_eval"
    base = "e"
    join_clause = dedent(
        """\
        join ps_adm_appl_eval e on
            a.adm_appl_nbr = e.adm_appl_nbr and
            a.emplid = e.emplid and
            a.acad_career = e.acad_career and
            a.stdnt_car_nbr = e.stdnt_car_nbr
        """
    )


class Relationship(PSTestCase):
    record = "ps_relationships"
    base = "r"
    join_clause = dedent(
        """\
        cross apply (
          select
            *
          from ps_relationships x
          where
            x.emplid = a.emplid and
            x.relationship_nbr = (
              select max(relationship_nbr) 
              from ps_relationships 
              where 
                name = x.name and 
                emplid = x.emplid and
                people_relation = x.people_relation
            )
        ) r
        """
    )


class Residency(PSTestCase):
    record = "ps_residency_off"
    base = "r"
    join_clause = dedent(
        """\
        join ps_residency_off r on 
          r.emplid = a.emplid and 
          r.acad_career = a.acad_career and 
          r.effective_term = (select max(admit_term) from ps_adm_appl_prog where adm_appl_nbr = a.adm_appl_nbr)
        """
    )


class ExtraCurricularActivity(PSTestCase):
    record = "ps_extracur_actvty"
    base = "e"
    join_clause = "join ps_extracur_actvty e on e.emplid = a.emplid"


class GeneralMaterials(PSTestCase):
    record = "ps_genl_materials"
    base = "m"
    join_clause = "join ps_genl_materials m on m.emplid = a.emplid"


class AcademicInterests(PSTestCase):
    record = "ps_adm_interests"
    base = "i"
    join_clause = dedent(
        """\
        cross apply (
          select
            listagg(ext_subject_area, ', ') within group (order by ext_subject_area) as ext_subject_area,
            max(effdt) as effdt,
            max(ls_data_source) as ls_data_source
          from ps_adm_interests x
          where
            x.emplid = a.emplid and
            x.acad_career = a.acad_career and
            x.effdt = (select max(effdt) from ps_adm_interests where emplid = x.emplid and acad_career = x.acad_career)
          ) i
        """
    )


class RecruitmentCategory(PSTestCase):
    record = "ps_adm_appl_rcr_ca"
    base = "c"
    join_clause = dedent(
        """\
        join ps_adm_appl_rcr_ca c on 
          c.emplid = a.emplid and 
          c.adm_appl_nbr = a.adm_appl_nbr and 
          c.stdnt_car_nbr = a.stdnt_car_nbr and
          c.acad_career = a.acad_career
        """
    )


class HonorsAndAwards(PSTestCase):
    record = "ps_honor_award_cs"
    base = "awd"
    join_clause = "join ps_honor_award_cs awd on a.emplid = awd.emplid"


class Languages(PSTestCase):
    record = "ps_accomplishments"
    base = "l"
    join_clause = dedent(
        """\
        join ps_accomplishments l on a.emplid = l.emplid
        join ps_scc_lang_vw x on l.accomplishment = x.accomplishment
        """
    )

    @property
    def sql_export(self) -> str:
        if self.field == "descr":
            return "x.descr"
        return super().sql_export


def build_case(destination: str, **kwargs) -> PSTestCase:
    destinations = {
        "additional data": AdditionalData,
        "application data": AdmApplData,
        # todo: checklist
        # todo: checklist item
        "academic interests": AcademicInterests,
        "citizenship": Citizenship,
        # todo: comm code
        "current address": CurrentAddress,
        "general materials": GeneralMaterials,
        "ethnicity": Ethnicity,
        "evaluation code": EvaluationCode,
        "extracurricular activity": ExtraCurricularActivity,
        "honors & awards": HonorsAndAwards,
        "languages": Languages,
        "residency": Residency,
        "relationship": Relationship,
        "other name": OtherName,
        "permanent address": PermanentAddress,
        "personal data": Person,
        "personal data effdt": PersonDataEffdt,
        "phone": Phone,
        "primary name": PrimaryName,
        "program data": AdmApplProg,
        "rating component": RatingComponent,
        "recruitment category": RecruitmentCategory,
        "school": School,
        "ssn": NationalID,
        "visa": Visa,
    }
    destination_class = destinations.get(destination.lower())
    return destination_class(export="", **kwargs)
