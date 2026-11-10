from types import ModuleType

from slixmpp.plugins import xep_0082
from slixmpp.plugins.base import (
    BasePlugin as BasePlugin,
    PluginManager as PluginManager,
    PluginNotFound as PluginNotFound,
)

__all__ = [
    "PLUGINS",
    "BasePlugin",
    "PluginManager",
    "PluginNotFound",
    "load_plugin",
    "register_plugin",
    "xep_0082",
]

PLUGINS: list[str]

# fmt: off

def load_plugin(
    name: str,
    module: str | ModuleType | None = ...,
) -> None: ...

def register_plugin(
    impl: type[BasePlugin],
    name: str | None = ...,
) -> None: ...

# fmt: on
