import os
import sys
import time

from app import create_app
from config import app_config

if __name__ == "__main__":
    test_plan = os.getenv("TEST_PLAN")
    config = app_config[test_plan]
    app = create_app(config)
    if "--loop" in sys.argv:
        while True:
            app.run()
            print("Sleeping...")
            time.sleep(180)
    elif "--reset" in sys.argv:
        print("Resetting all tests...")
        app.publisher.reset_tests()
        exit()
    else:
        app.run()
