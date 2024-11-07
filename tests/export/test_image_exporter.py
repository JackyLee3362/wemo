from entity.moment_msg import MomentMsg
from export.image_exporter import ImageExporter
from pathlib import Path
import xmltodict
import pytest


@pytest.fixture
def msg():
    cur_dir = Path(__file__).parent
    file_path = cur_dir.parent.joinpath("res", "test_random.xml")
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    xml = content
    msg_dict = xmltodict.parse(xml, force_list={"media"})
    momentMsg: MomentMsg = MomentMsg.from_dict(msg_dict)
    return momentMsg


def test_image_exporter_by_xml(msg: MomentMsg):
    exp = ImageExporter()
    exp.handle_moment_msg(msg)
