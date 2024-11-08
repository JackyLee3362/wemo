from model.moment_msg import MomentMsg, parse_xml
from export.image_exporter import ImageExporter
from pathlib import Path
import pytest


@pytest.fixture
def msg():
    cur_dir = Path(__file__).parent
    file_path = cur_dir.parent.joinpath("res", "test_random.xml")
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    xml = content
    moment = parse_xml(xml)
    return moment


def test_image_exporter_by_xml(msg: MomentMsg):
    exp = ImageExporter()
    exp.handle_image_from_moment(msg)
