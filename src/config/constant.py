from pathlib import Path


# 路径配置
PROJECT_DIR = Path(__file__).resolve().parent.parent.parent
SRC_DIR = PROJECT_DIR.joinpath("src")
DATA_DIR = PROJECT_DIR.joinpath("data")
CONFIG_DIR = PROJECT_DIR.joinpath("config")
LOG_DIR = PROJECT_DIR.joinpath("logs")


