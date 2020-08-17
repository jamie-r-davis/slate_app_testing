import os

from dotenv import load_dotenv

load_dotenv()


class Config:
    DEBUG = True
    DB_URL = os.getenv("DB_URL")
    GSPREAD_CREDENTIAL = os.getenv("GSPREAD_CREDENTIAL")
    GSPREAD_SHEET_KEY = os.getenv("GSPREAD_SHEET_KEY")
    GSPREAD_WORKSHEET_NAME = os.getenv("GSPREAD_WORKSHEET_NAME")
