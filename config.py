import os

from dotenv import load_dotenv

load_dotenv()


class Config:
    DEBUG = bool(os.getenv("DEBUG", True))
    DB_URL = os.getenv("DB_URL")
    PS_DB_URL = os.getenv("PS_DB_URL")
    GSPREAD_CREDENTIAL = os.getenv("GSPREAD_CREDENTIAL")
    GSPREAD_WORKSHEET_NAME = "Test Cases"
    COL_INDEXES = {"status": 2, "actual": 9, "comment": 10}
    SLEEP_INTERVAL = int(os.getenv("SLEEP_INTERVAL", 90))


class DefaultConfig(Config):
    TEST_PLAN = "default"


class CommonAppConfig(Config):
    TEST_PLAN = "commonapp"
    TEST_MODE = "slate"
    GSPREAD_SHEET_KEY = os.getenv(
        "COMMONAPP_SHEET_KEY", "1kZZbbbnzxGBDsLIM_2XX27wfHQL_rnSw6FfhTRkXD2s"
    )


class PSConfig(CommonAppConfig):
    TEST_PLAN = "peoplesoft"
    TEST_MODE = "peoplesoft"
    GSPREAD_SHEET_KEY = os.getenv("PEOPLESOFT_SHEET_KEY")
    GSPREAD_WORKSHEET_NAME = "PS Test Cases"
    # DB_URL = os.getenv("PS_DB_URL") or os.getenv("DB_URL")
    COL_INDEXES = {"status": 2, "actual": 9, "comment": 10}


class CoalitionConfig(Config):
    TEST_PLAN = "coalition"
    TEST_MODE = "slate"
    GSPREAD_SHEET_KEY = os.getenv(
        "COALITION_SHEET_KEY", "1brajclYopMFzAycKeOKWf5-CZk417XZL1C0QH4TRUUA"
    )


class CommonAppTransferConfig(Config):
    TEST_PLAN = "commonapp_transfer"
    TEST_MODE = "slate"
    GSPREAD_SHEET_KEY = os.getenv(
        "COMMONAPP_TRANSFER_SHEET_KEY", "1IPQPZec3R42AEjT0DGGfCs35c6wkmeKO31p071kJLKM"
    )


app_config = {
    "commonapp": CommonAppConfig,
    "coalition": CoalitionConfig,
    "commonapp_transfer": CommonAppTransferConfig,
    "peoplesoft": PSConfig,
}
