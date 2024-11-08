import sys

sys.path.insert(0, 'src')
from app import Application

if __name__ == "__main__":
    app = Application()
    app.run()
