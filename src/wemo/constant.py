# import sys
from pathlib import Path

# app setting
PROJECT_DIR = Path(__file__).resolve().parent.parent.parent
SRC_DIR = PROJECT_DIR.joinpath("src")
DATA_DIR = PROJECT_DIR.joinpath("data")
CONFIG_DIR = PROJECT_DIR.joinpath("config")
LOG_DIR = PROJECT_DIR.joinpath("logs")
MOCK_DIR = PROJECT_DIR.joinpath("mock")
BIN_DIR = PROJECT_DIR.joinpath("bin")

# if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
#     BIN_DIR = Path(__file__).resolve().parent.parent.joinpath("bin")
# else:
#     BIN_DIR = PROJECT_DIR.joinpath("bin")
