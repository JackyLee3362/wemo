from wemo.base.constant import PROJECT_DIR
from wemo.export.feed_exporter import MarkdownExporter
from wemo.model.dto import MomentMsg
from wemo.model.user import User

wxid = "test_export"
user = User.mock_user(wxid)


def test_exporter():
    with open(PROJECT_DIR.joinpath("tests", "static", wxid + ".xml")) as f:
        xml = f.read()

    moment = MomentMsg.parse_xml(xml)

    me = MarkdownExporter(user)

    res1 = me.find_imgs(moment)
    print("img:", res1)
    res2 = me.find_videos(moment)
    print("video:", res2)
    res3 = me.find_avater(moment)
    print("avatar:", res3)
