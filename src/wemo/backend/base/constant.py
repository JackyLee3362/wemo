from pathlib import Path
from wemo.backend.utils.helper import get_root_path
import sys

if getattr(sys, "frozen", False):
    PROJECT_DIR = Path(sys.executable).parent
else:
    PROJECT_DIR = Path(get_root_path("wemo")).parent.parent

SRC_DIR = PROJECT_DIR.joinpath("src")
DATA_DIR = PROJECT_DIR.joinpath("data")
CONFIG_DIR = PROJECT_DIR.joinpath("config")
LOGS_DIR = PROJECT_DIR.joinpath("logs")
MOCK_DIR = PROJECT_DIR.joinpath("mock")
OUTPUT_DIR = PROJECT_DIR.joinpath("output")
BIN_DIR = PROJECT_DIR.joinpath("bin")
STATIC_DIR = PROJECT_DIR.joinpath("static")
