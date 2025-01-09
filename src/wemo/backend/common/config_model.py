from dataclasses import dataclass

# 将 app.toml 映射到 ConfigModel 类中
# 暂时未使用，可以考虑使用 dynaconfig 库实现动态配置管理


@dataclass
class ConfigModel:
    class App:
        name: str
        version: str

    class Logging:
        level: str

    class User:
        wxid: str
        key: str
        wx_dir: str

    app: App
    logging: Logging
