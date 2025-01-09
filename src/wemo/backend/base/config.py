from __future__ import annotations

import tomllib  # Python 3.11+

__all__ = ("TomlConfig",)


class _AttrDict(dict):
    """A dict-like object with attribute access."""

    def __getitem__(self, key: str):
        """Access dict values by key."""
        value = super().__getitem__(key)
        if isinstance(value, dict):
            self[key] = value = _AttrDict(value)
        return value

    def __getattr__(self, key: str) -> object:
        """Get dict values as attributes.

        :param key: key to retrieve
        """
        return self[key]

    def __setattr__(self, key: str, value: object):
        """Set dict values as attributes.

        :param key: key to set
        :param value: new value for key
        """
        self[key] = value
        return


class TomlConfig(_AttrDict):
    """Store data from TOML configuration files."""

    def __init__(self, paths=None, root=None, params=None):
        """Initialize this object.

        :param paths: one or more config file paths to load
        :param root: place config values at this root
        :param params: mapping of parameter substitutions
        """
        super().__init__()
        if paths:
            self.load_file(paths, root, params)
        return

    def load_file(self, path, default_config: dict = {}):
        """Load data from configuration files.

        Configuration values are read from a sequence of one or more TOML
        files. Files are read in the given order, and a duplicate value will
        overwrite the existing value. If a root is specified the config data
        will be loaded under that attribute.

        :param paths: one or more config file paths to load
        :param root: place config values at this root
        :param params: mapping of parameter substitutions
        """
        with open(path, "rb") as f:
            data = tomllib.load(f)
        if default_config:
            self.setdefault(default_config).update(data)
        else:
            self.update(data)
