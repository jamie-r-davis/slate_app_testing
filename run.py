import sys
import time

from app import app

if __name__ == "__main__":
    if "--loop" in sys.argv:
        while True:
            app.run()
            print("Sleeping...")
            time.sleep(180)
    else:
        app.run()
