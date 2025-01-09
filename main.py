import sys

sys.path.append("src")

from wemo.app import App

if __name__ == "__main__":
    app = App("wemo")
    app.run()
