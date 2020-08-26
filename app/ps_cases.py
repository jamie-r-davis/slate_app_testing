from textwrap import dedent

from .cases import BaseTestCase


class PSTestCase(BaseTestCase):
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
              a.ext_adm_appl_nbr = '{self.external_id}'"""
        if self.filters:
            sql += f" and {self.filters}"
        return dedent(sql)


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
    join_clause = "join ps_pers_data_effdt pde on a.emplid = pde.emplid and pde.effdt = (select max(effdt) from ps_pers_data_effdt where emplid = pde.emplid)"


class AdditionalData(PSTestCase):
    record = "ps_m_ra_adl_data"
    base = "adl"
    join_clause = "join ps_m_ra_adl_data adl on a.emplid = adl.emplid and a.adm_appl_nbr = adl.adm_appl_nbr and a.acad_career = adl.acad_career and a.stdnt_car_nbr = adl.stdnt_car_nbr"


class NationalID(PSTestCase):
    record = "ps_pers_nid"
    base = "nid"
    join_clause = "join ps_pers_nid nid on a.emplid = nid.emplid"

    @property
    def sql_export(self) -> str:
        if self.field == "national_id":
            return "regexp_replace(national_id, '^[0-9]{5}', 'XXXXX')"
        return super().sql_export


def build_case(destination: str, **kwargs) -> PSTestCase:
    destinations = {
        "additional data": AdditionalData,
        "application data": AdmApplData,
        "current address": CurrentAddress,
        "other name": OtherName,
        "permanent address": PermanentAddress,
        "personal data": Person,
        "personal data effdt": PersonDataEffdt,
        "primary name": PrimaryName,
        "program data": AdmApplProg,
        "ssn": NationalID,
    }
    destination_class = destinations.get(destination.lower())
    return destination_class(export="", **kwargs)
