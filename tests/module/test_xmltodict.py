import xmltodict


def test_parse_xml_string():
    xml = """<a prop="x"><b>1</b><b>2</b></a>"""
    parsed_dict = xmltodict.parse(xml)
    assert parsed_dict["a"] is not None

    xml = """<a prop="x"><b>1</b><b>2</b><media>test_media</media></a>"""
    msg_dict = xmltodict.parse(xml, force_list={"media"})
    assert msg_dict is not None
    assert isinstance(msg_dict["a"]["media"], list)
