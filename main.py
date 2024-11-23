import sys
import os

from wemo.app import App

sys.path.append("./src")
os.environ.setdefault("WEMO_DEBUG", "true")


if __name__ == "__main__":
    app = App(__name__)
    app.run()
