from wemo.backend.common.constant import PROJECT_DIR
from wemo.backend.render.render_service import RenderService
from wemo.backend.common.model import MomentMsg
from wemo.backend.ctx import Context

wxid = "test_export"
user = Context.mock_ctx(wxid)


def test_exporter():
    with open(PROJECT_DIR.joinpath("tests", "static", wxid + ".xml")) as f:
        xml = f.read()
    moment = MomentMsg.parse_xml(xml)
    rs = RenderService(user)
