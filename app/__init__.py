from config import Config

from .executor import TestExecutor
from .publishers import GoogleSheetsPublisher

publisher = GoogleSheetsPublisher.from_config(Config)
app = TestExecutor(Config, publisher)
