from pathlib import Path
import xmltodict
from entity.moment_msg import MomentMsg


def test_xml_1():
    xml = """<a prop="x"><b>1</b><b>2</b></a>"""
    parsed_dict = xmltodict.parse(xml)
    assert parsed_dict["a"] is not None


def test_xml_2():
    xml = """<a prop="x"><b>1</b><b>2</b><media>test_media</media></a>"""
    msg_dict = xmltodict.parse(xml, force_list={"media"})
    assert msg_dict is not None
    assert isinstance(msg_dict["a"]["media"], list)
    print(msg_dict)


def test_xml_parse_moment():
    cur_dir = Path(__file__).parent
    file_path = cur_dir.parent.joinpath("res", "test_random.xml")
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    xml = content
    msg_dict = xmltodict.parse(xml, force_list={"media"})
    momentMsg: MomentMsg = MomentMsg.from_dict(msg_dict)
    assert momentMsg is not None
