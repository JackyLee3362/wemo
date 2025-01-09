from wemo.backend.base.config import TomlConfig
from wemo.backend.common import constant
from wemo.backend.common.constant import MOCK_DIR
from wemo.backend.common.model import MomentMsg, TimelineObject
from wemo.backend.ctx import Context
from wemo.backend.database.micro_msg import Contact, ContactHeadImgUrl, ContactLabel
from wemo.backend.database.sns import Comment, SnsConfig


def mock_ctx(wxid: str) -> Context:
    proj_path = constant.PROJECT_DIR
    config = TomlConfig()
    config.load_file(constant.CONFIG_DEFAULT_FILE)
    wx_user_dir = MOCK_DIR.joinpath(wxid)
    info = {"wxid": wxid, "key": None, "wx_dir": wx_user_dir}

    return Context(
        root=proj_path,
        config=config,
        extra=info,
    )


def mock_timeline_object():
    return TimelineObject(
        id=0,
        username="mock-from-time-object",
        location=None,
        ContentObject=None,
        createTime=1730123456,
        contentDesc="",
    )


def mock_user(n):
    return f"wxid_{n}"


def mock_url(n):
    return f"https://example.com/{n}"


def mock_bytes(size=1024):
    return bytes(random.getrandbits(8) for _ in range(size))


def mock_timestamp():
    return int(time.time()) + random.randint(0, 100000)


def mock_sns_content():
    return ""


def mock_comment(seed):
    random.seed(seed)
    return Comment(
        feed_id=-mock_timestamp() * 10,
        comment_id=-mock_timestamp() * 10 + 1,
        create_time=mock_timestamp(),
        flag=0,
        comment_type=1,
        comment_flag=0,
        content="mock comment" + str(seed),
        from_username=mock_user(seed + 1),
        reply_id=0,
        reply_username=0,
        del_flag=0,
        comment_id_64=0,
        reply_id_64=0,
        is_ad=0,
    )


def mock_sns(seed):
    return SnsConfig(key=str(seed), i_val="Ivalue" + str(seed))


def mock_moment_msg():
    return MomentMsg(mock_timeline_object())


def mock_contact(seed):
    random.seed(seed)
    user = mock_user(seed)
    alias = None
    if seed % 2 == 0:
        alias = "alias:" + user

    return Contact(
        username=user,
        alias=alias,
        del_flag=0,
        type=3,
        verify_flag=0,  # 0 表示是好友
    )


def mock_contant_head_img_url(seed):
    random.seed(seed)
    username = mock_user(seed)
    url = mock_url(seed)
    return ContactHeadImgUrl(
        username=username,
        small_url=url,
        big_url=url + "bigHead",
        r0=0,
    )


def mock_contact_label(seed):
    names = {0: "默认", 1: "家人", 2: "朋友", 3: "同事", 4: "同学", 5: "其他"}
    if seed not in names.keys():
        raise ValueError("seed too large")
    return ContactLabel(label_id=seed, label_name=names[seed])
