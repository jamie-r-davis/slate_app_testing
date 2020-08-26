from config import Config

from .executor import TestExecutor
from .publishers import GoogleSheetsPublisher


def create_app(config: Config):
    publisher = GoogleSheetsPublisher.from_config(config)
    app = TestExecutor(config, publisher)
    return app
