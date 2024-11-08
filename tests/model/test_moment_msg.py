from pathlib import Path
import xmltodict
from model.moment_msg import MomentMsg, parse_xml
import xml.etree.ElementTree as ET


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
        xml = f.read()
    momentMsg = parse_xml(xml)
    assert momentMsg is not None

    tree = ET.parse(file_path)
    print(tree)


def test_xml_parse_error():
    cur_dir = Path(__file__).parent
    file_path = cur_dir.parent.joinpath("res", "test_1.xml")
    with open(file_path, "r", encoding="utf-8") as f:
        xml = f.read()
    momentMsg = parse_xml(xml)
    assert momentMsg is not None
