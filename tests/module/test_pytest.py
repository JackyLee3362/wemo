def setup_module():
    print("测试模块准备")


def teardown_module():
    print("测试模块清理")


def setup_function():
    print("测试函数准备")


def teardown_function():
    print("测试函数清理")


def test_add():  # 测试函数
    """测试加法"""
    s = 1 + 2
    assert s == 3, f"断言失败, {s} != 3"  # 断言
