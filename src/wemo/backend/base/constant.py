from pathlib import Path
from wemo.backend.utils.helper import get_root_path

# app setting
PROJECT_DIR = Path(get_root_path("wemo")).parent.parent
SRC_DIR = PROJECT_DIR.joinpath("src")
DATA_DIR = PROJECT_DIR.joinpath("data")
CONFIG_DIR = PROJECT_DIR.joinpath("config")
LOGS_DIR = PROJECT_DIR.joinpath("logs")
MOCK_DIR = PROJECT_DIR.joinpath("mock")
OUTPUT_DIR = PROJECT_DIR.joinpath("output")
BIN_DIR = PROJECT_DIR.joinpath("bin")
STATIC_DIR = PROJECT_DIR.joinpath("static")

# if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
#     BIN_DIR = Path(__file__).resolve().parent.parent.joinpath("bin")
# else:
#     BIN_DIR = PROJECT_DIR.joinpath("bin")
