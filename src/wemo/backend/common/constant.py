import sys
from pathlib import Path

PROJECT_DIR = Path(sys.modules["wemo"].__file__).parent.parent.parent

SRC_DIR = PROJECT_DIR.joinpath("src")
DATA_DIR = PROJECT_DIR.joinpath("data")

CONFIG_DIR = PROJECT_DIR.joinpath("config")
CONFIG_DEFAULT_FILE = CONFIG_DIR.joinpath("app.toml")

LOGS_DIR = PROJECT_DIR.joinpath("logs")
MOCK_DIR = PROJECT_DIR.joinpath("mock")
OUTPUT_DIR = PROJECT_DIR.joinpath("output")
BIN_DIR = PROJECT_DIR.joinpath("bin")
STATIC_DIR = PROJECT_DIR.joinpath("static")
TEMPLATE_DIR = PROJECT_DIR.joinpath("template")
